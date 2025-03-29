from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import depolarizing_error

class QuantumBB84:
    def __init__(self, key_length=10, eve_present=False, noise_level=0):
        self.key_length = key_length
        self.simulator = Aer.get_backend('qasm_simulator')
        self.eve_present = eve_present
        self.noise_level = noise_level
        self.alice_bits = []
        self.alice_bases = []
        self.bob_bits = []
        self.bob_bases = []
        self.alice_shared_key = []
        self.bob_shared_key = []

    def _quantum_random_bits(self, n):
        qc = QuantumCircuit(n, n)
        for i in range(n):
            qc.h(i)
        qc.measure(range(n), range(n))
        result = self.simulator.run(transpile(qc, self.simulator), shots=1).result()
        return [int(bit) for bit in list(result.get_counts().keys())[0][::-1]]

    def _add_noise(self):
        noise_model = NoiseModel()
        error = depolarizing_error(self.noise_level, 1)
        noise_model.add_all_qubit_quantum_error(error, ['h', 'x'])
        return noise_model

    def alice_prepare(self):
        self.alice_bits = self._quantum_random_bits(self.key_length)
        self.alice_bases = self._quantum_random_bits(self.key_length)
        qc = QuantumCircuit(self.key_length, self.key_length)
        for i in range(self.key_length):
            if self.alice_bits[i] == 1:
                qc.x(i)
            if self.alice_bases[i] == 1:
                qc.h(i)
        return transpile(qc, self.simulator, optimization_level=0)

    def eve_eavesdrop(self, qc):
        eve_bases = self._quantum_random_bits(self.key_length)
        for i in range(self.key_length):
            if eve_bases[i] == 1:
                qc.h(i)
        qc.measure(range(self.key_length), range(self.key_length))
        result = self.simulator.run(qc, shots=1).result()
        eve_bits = [int(bit) for bit in list(result.get_counts().keys())[0][::-1]]
        
        qc = QuantumCircuit(self.key_length, self.key_length)
        for i in range(self.key_length):
            if eve_bits[i] == 1:
                qc.x(i)
            if eve_bases[i] == 1:
                qc.h(i)
        return transpile(qc, self.simulator, optimization_level=0)

    def bob_measure(self, qc):
        self.bob_bases = self._quantum_random_bits(self.key_length)
        for i in range(self.key_length):
            if self.bob_bases[i] == 1:
                qc.h(i)
        qc.measure(range(self.key_length), range(self.key_length))
        if self.noise_level > 0:
            noise_model = self._add_noise()
            result = self.simulator.run(qc, noise_model=noise_model, shots=1).result()
        else:
            result = self.simulator.run(qc, shots=1).result()
        self.bob_bits = [int(bit) for bit in list(result.get_counts().keys())[0][::-1]]

    def generate_key(self):
        self.alice_shared_key = []
        self.bob_shared_key = []
        for i in range(self.key_length):
            if self.alice_bases[i] == self.bob_bases[i]:
                self.alice_shared_key.append(self.alice_bits[i])
                self.bob_shared_key.append(self.bob_bits[i])

    def encrypt(self, message, key):
        if not key:
            return ""
        return ''.join([chr(ord(c) ^ key[i % len(key)]) for i, c in enumerate(message)])

    def run(self, message):
        alice_qc = self.alice_prepare()
        
        if self.eve_present:
            alice_qc = self.eve_eavesdrop(alice_qc)
        
        self.bob_measure(alice_qc)
        self.generate_key()
        
        if not self.alice_shared_key or not self.bob_shared_key:
            print("⚠️ Error: No shared key!")
            return
        
        if self.alice_shared_key != self.bob_shared_key:
            print("❌ Error detected in the key. Possible eavesdropping or noise. Aborting.")
            return
        
        encrypted = self.encrypt(message, self.alice_shared_key)
        decrypted = self.encrypt(encrypted, self.alice_shared_key)
        
        print("\n" + "═"*50)
        print(f"🔐 Key Length: {len(self.alice_shared_key)}")
        print(f"👩🔬 Alice's Bases: {self.alice_bases}")
        print(f"👨🔬 Bob's Bases:   {self.bob_bases}")
        print(f"🔑 Shared Key: {self.alice_shared_key}")
        print("\n📨 Original Message:", message)
        print("🔒 Encrypted Message:", encrypted)
        print("🔓 Decrypted Message:", decrypted)
        print("\nResult:", "✅ SUCCESS" if decrypted == message else "❌ FAILURE")