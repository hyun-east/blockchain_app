import hashlib
import json
from time import time
import requests

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set() # 네트워크 내의 노드들을 저장하는 집합
        self.new_block(previous_hash='1', proof=100) # 제네시스 블록 생성

    def register_node(self, address):
        """
        네트워크에 새로운 노드를 추가하는 메소드
        """
        self.nodes.add(address)

    def valid_chain(self, chain):
        """
        체인이 유효한지 확인하는 메소드
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        네트워크 내의 충돌(분쟁)을 해결하는 메소드
        가장 긴 체인이 유효하다고 간주
        """
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash=None):
        """
        새로운 블록을 생성하고 체인에 추가하는 메소드
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, medicine, quantity, price):
        """
        새로운 거래를 생성하여 다음에 채굴될 블록에 추가하는 메소드
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'medicine': medicine,
            'quantity': quantity,
            'price': price,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        블록의 SHA-256 해시값을 생성하는 메소드
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        체인의 마지막 블록을 반환하는 메소드
        """
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        새로운 블록을 채굴하기 위한 작업 증명 메소드
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        작업 증명이 유효한지 확인하는 메소드
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
