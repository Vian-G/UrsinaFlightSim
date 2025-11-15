from matrix import Matrix

#  matrix tests
m1_ = Matrix([[1, 2], [3, 4]])
m2_ = Matrix([[5, 6], [7, 8]])

# Basic functionality tests
print(" Height OK" if m1_.getheight() == 2 else " Height FAIL")
print(" Width OK" if m1_.getwidth() == 2 else " Width FAIL")
print(" Data OK" if m1_.getmatrix() == [[1, 2], [3, 4]] else " Data FAIL")
print(" Add OK" if (m1_ + m2_).getmatrix() == [[6, 8], [10, 12]] else " Add FAIL")
print(" Mul OK" if (m1_ * m2_).getmatrix() == [[19, 22], [43, 50]] else " Mul FAIL")
print(" Scalar OK" if (m1_ * 2).getmatrix() == [[2, 4], [6, 8]] else " Scalar FAIL")
print(" Det OK" if m1_.det() == -2 else " Det FAIL")
print(" Sub OK" if m1_.sub(0, 0).getmatrix() == [[4]] else " Sub FAIL")
print()

# Error handling tests for 
try:
    Matrix([])  # Empty list
    print(" Empty list: FAIL")
except ValueError:
    print(" Empty list: OK")

try:
    Matrix([[1, 2], [3]])  # Unequal rows
    print(" Unequal rows: FAIL")
except ValueError:
    print(" Unequal rows: OK")

try:
    Matrix([[1, "2"], [3, 4]])  # Non-numeric
    print(" Non-numeric: FAIL")
except ValueError:
    print(" Non-numeric: OK")

try:
    Matrix([1, 2])  # Non-2D list
    print(" Non-2D: FAIL")
except ValueError:
    print(" Non-2D: OK")

try:
    m1_.sub("0", 0)  # Invalid submatrix type
    print(" Sub bad type: FAIL")
except TypeError:
    print(" Sub bad type: OK")

try:
    m1_.sub(2, 0)  # Invalid submatrix index
    print(" Sub bad index: FAIL")
except IndexError:
    print(" Sub bad index: OK")

try:
    m1_ + 5  # Invalid addition type
    print(" Add bad type: FAIL")
except TypeError:
    print(" Add bad type: OK")

try:
    m1_ * "2"  # Invalid scalar type
    print(" Scalar bad type: FAIL")
except TypeError:
    print(" Scalar bad type: OK")

input()

