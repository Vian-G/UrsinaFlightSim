from random import randint

#############################################################
########### PASSWORD HASH AND SALTING FUNCTIONS #############
#############################################################
    
def generate_salt():
    """
    Generates a random salt value for password hashing.
    Cybersecurity best practice: unique salt for each password.
    """
    return randint(31, 2**32 - 1)           # Generates a random salt in the 32-bit range

def hash_password(password, salt):
    """
    Custom password hashing algorithm implementation.
    Demonstrates cryptographic concepts for password security:
    - Salting: adds random value to prevent rainbow table attacks
    - Multiple transformations: bitwise XOR, binary shifts, and addition
    - Modulo prime: keeps hash value in manageable range
    """

    if not isinstance(password, str):
        raise TypeError("Password must be a string")
    if not isinstance(salt, int):
        raise TypeError("Salt must be an integer")
    if salt < 0:
        raise ValueError("Salt cannot be negative")
    
    hash_val = 867243217                    # Initial large "seed" prime
    for char in password:
        char = ord(char)                    # Convert from character to ASCII integer value
        hash_val = hash_val * 97            # Multiply by prime
        hash_val = hash_val ^ (char + 144479) # Imprint the ASCII value - Bitwise XOR 
        hash_val = hash_val <<((char%5) + 1)  # Imprint the ASCII value - Binary shift
        hash_val = hash_val ^ salt          # Imprint the salt value - Bitwise XOR
        hash_val = hash_val + salt          # Imprint the salt value - ADD
        
    hash_val = hash_val % 387942806485727   # Mod by prime to ensures value fits in 63 bits
    return abs(hash_val)                    # Return the hash



