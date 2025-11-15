#############################################################
###################### MATRIX CLASS #########################
#############################################################

class Matrix:
    """
    Custom Matrix implementation for linear algebra operations.
    Used for flight physics calculations (state-space model).
    Demonstrates OOP concepts like Encapsulation and Polymorphism.
    """
    def __init__(self, data):
        # Defensive Programming
        # data is expected as a 2D list (list of rows)
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Input must be a non-empty 2D list")
        
        # Check if each element is a list
        for row in data:
            if not isinstance(row, list):
                raise ValueError("All elements must be lists")
        
        # Check if all rows have the same length
        width = len(data[0])
        for row in data:
            if len(row) != width:
                raise ValueError("All rows must have the same length")
        
        # Check if all elements are numbers
        for row in data:
            for x in row:
                if not isinstance(x, (int, float)):
                    raise ValueError("All elements must be numbers")
                    
        self.data = data
        self.height = len(data)
        self.width = len(data[0]) if self.height > 0 else 0

    # Next 3 functions demonstrate the OOP principle of Encapsulation
    # by providing controlled access to private attributes
    
    def getmatrix(self):
        return self.data

    def getheight(self):
        return self.height

    def getwidth(self):
        return self.width

    def sub(self, x, y):
        """
        Creates a submatrix by removing specified row and column.
        Used in determinant calculation with the recursive minor method.
        """
        # Defensive Programming
        if not isinstance(y, int) or not isinstance(x, int):
            raise TypeError("Indices must be integers")
        if not (0 <= y < self.width and 0 <= x < self.height):
            raise IndexError("Indices out of bounds")
        r = []
        for i in range(self.height):
            if i != x:
                u = []
                for j in range(self.width):
                    if j != y:
                        u.append(self.data[i][j])
                r.append(u)
        return Matrix(r)

    def det(self):
        """
        Recursive determinant calculation using the Laplace expansion.
        Demonstrates advanced math concept - matrix determinants.
        Base case: 1x1 matrix determinant is the value itself.
        Recursive case: Sum of products of elements and cofactors.
        """
        if self.height != self.width:
            raise ValueError("Matrix must be square for determinant")
        if self.width == 1:
            return self.data[0][0]
        else:
            t = 0
            for i in range(self.height):
                # Calculate cofactor using submatrix
                submatrix = self.sub(0, i)
                # Laplace expansion formula: element * cofactor * sign

                # Debug Line Below
                # print(f'{t} += {self.data[0][i]} * det({submatrix}) * {((-1)**i)}')

                t += self.data[0][i] * submatrix.det() * ((-1)**i)
            return t
    
    # Operator overloading demonstrates OOP principle of Polymorphism
    # Allows matrices to be used with standard Python operators "+" and "*"
    def __add__(self, other):
        """
        Overloads + operator for matrix addition.
        Polymorphism - changing behavior of standard operator.
        """
        # Defensive Programming
        if not isinstance(other, Matrix):
            raise TypeError("Can only add Matrix with another Matrix")
        if self.height != other.height or self.width != other.width:
            raise ValueError("Matrices must have same dimensions for addition")
        result = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(self.data[i][j] + other.data[i][j])
            result.append(row)
        return Matrix(result)

    def __mul__(self, other):
        """
        Overloads * operator for matrix multiplication.
        Supports both matrix-matrix and matrix-scalar multiplication.
        Polymorphism - operator behavior changes based on operand type.
        """
        # If multiplying by another matrix:
        
        if isinstance(other, Matrix):
            # Defensive Programming
            if self.width != other.height:
                raise ValueError("Matrix dimensions incompatible for multiplication")
            result = []
            for i in range(self.height):
                row = []
                for j in range(other.width):
                    sum_val = 0
                    for k in range(self.width):
                        sum_val += self.data[i][k] * other.data[k][j]
                    row.append(sum_val)
                result.append(row)
            return Matrix(result)
        # Scalar multiplication
        elif isinstance(other, (int, float)):
            result = []
            for i in range(self.height):
                row = []
                for j in range(self.width):
                    row.append(self.data[i][j] * other)
                result.append(row)
            return Matrix(result)
        else:
            raise TypeError("Multiplication only supported with Matrix or scalar")

    def __rmul__(self, other):
        """
        Overloads right multiplication to support scalar * matrix syntax.
        Polymorphism - enables commutative property for scalar multiplication.
        """
        if not isinstance(other, (int, float)):
            raise TypeError("Right multiplication only supported with scalar")
        return self.__mul__(other)

    def __str__(self): # String representation of the matrix for debugging.
        return f'Matrix({self.data})'
