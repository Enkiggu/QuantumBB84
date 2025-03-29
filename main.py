from q_bb84 import QuantumBB84

print("\nScenario 1: Secure Communication")
bb84_secure = QuantumBB84(key_length=8, eve_present=False, noise_level=0)
bb84_secure.run("Hello, World!")

print("\nScenario 2: Eavesdropping")
bb84_eve = QuantumBB84(key_length=12, eve_present=True, noise_level=0)
bb84_eve.run("Secret Message")

print("\nScenario 3: Noisy Channel %10")
bb84_noise = QuantumBB84(key_length=12, eve_present=False, noise_level=0.1)
bb84_noise.run("Test123")