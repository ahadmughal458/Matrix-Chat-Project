import numpy as np

class HillCipher:
    def __init__(self, key_matrix):
        """Initialize the cipher with a 3x3 key matrix."""
        self.key_matrix = np.array(key_matrix)
        self.n = self.key_matrix.shape[0]
        
        # 1. Check if Determinant is 0
        det = np.round(np.linalg.det(self.key_matrix))
        if det == 0:
            raise ValueError("ERROR: Matrix is Singular! Determinant is 0.")
            
        # 2. Calculate the Inverse Matrix
        self.inv_matrix = np.linalg.inv(self.key_matrix)

    def text_to_vectors(self, text):
        """Converts text to numbers and pads it to fit the 3x3 matrix."""
        numbers = [ord(c) for c in text]
        
        # Pad with spaces (ASCII 32) if the message doesn't divide evenly by 3
        while len(numbers) % self.n != 0:
            numbers.append(32)
            
        return np.array(numbers).reshape(-1, self.n).T

    def vectors_to_text(self, vectors):
        """Converts numbers back into readable text."""
        numbers = np.round(vectors.T.flatten()).astype(int)
        return ''.join([chr(num) for num in numbers])

    def encrypt(self, plaintext):
        """Matrix Multiplication (C = A * P)"""
        plain_vectors = self.text_to_vectors(plaintext)
        cipher_vectors = np.dot(self.key_matrix, plain_vectors)
        return cipher_vectors

    def decrypt(self, cipher_vectors):
        """Inverse Matrix Multiplication (P = A^-1 * C)"""
        decrypted_vectors = np.dot(self.inv_matrix, cipher_vectors)
        return self.vectors_to_text(decrypted_vectors)