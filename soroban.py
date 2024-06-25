def soroban_arithmetic(num1, num2, operation):
    result = 0
    multiplier = 1
    
    # 各演算に応じて処理を分岐する
    if operation == 'addition':
        carry = 0
        while num1 or num2 or carry:
            digit1 = num1 % 10
            digit2 = num2 % 10
            sum_digits = digit1 + digit2 + carry
            
            if sum_digits >= 10:
                carry = 1
                sum_digits -= 10
            else:
                carry = 0
            
            result += sum_digits * multiplier
            multiplier *= 10
            num1 //= 10
            num2 //= 10
        
    elif operation == 'subtraction':
        borrow = 0
        while num1 or num2:
            digit1 = num1 % 10
            digit2 = num2 % 10
            
            if digit1 < digit2 + borrow:
                difference = 10 + digit1 - digit2 - borrow
                borrow = 1
            else:
                difference = digit1 - digit2 - borrow
                borrow = 0
            
            result += difference * multiplier
            multiplier *= 10
            num1 //= 10
            num2 //= 10
    
    elif operation == 'multiplication':
        while num2:
            digit2 = num2 % 10
            num2 //= 10
            temp_result = 0
            carry = 0
            
            num1_copy = num1
            while num1_copy or carry:
                digit1 = num1_copy % 10
                product = digit1 * digit2 + carry
                carry = product // 10
                temp_result += (product % 10) * multiplier
                multiplier *= 10
                num1_copy //= 10
            
            result = soroban_addition(result, temp_result)
    
    elif operation == 'division':
        while num1 >= num2:
            temp_divisor = num2
            count = 1
            while num1 >= temp_divisor:
                num1 -= temp_divisor
                result = soroban_addition(result, count * multiplier)
                temp_divisor *= 10
                count += 1
            multiplier //= 10
    
    return result

# 加算の例
num1 = 123456789
num2 = 987654321
result_add = soroban_arithmetic(num1, num2, 'addition')
print(f"{num1} + {num2} = {result_add}")

# 減算の例
num1 = 987654321
num2 = 123456789
result_sub = soroban_arithmetic(num1, num2, 'subtraction')
print(f"{num1} - {num2} = {result_sub}")

# 乗算の例
num1 = 123
num2 = 456
result_mul = soroban_arithmetic(num1, num2, 'multiplication')
print(f"{num1} * {num2} = {result_mul}")

# 除算の例
num1 = 1000
num2 = 25
result_div = soroban_arithmetic(num1, num2, 'division')
print(f"{num1} / {num2} = {result_div}")

def soroban_decimal_addition(num1, num2):
    # 文字列として扱い、小数点以下の桁数を揃える
    str_num1, str_num2 = str(num1), str(num2)
    decimal_places1 = str_num1[::-1].find('.') if '.' in str_num1 else 0
    decimal_places2 = str_num2[::-1].find('.') if '.' in str_num2 else 0
    max_decimal_places = max(decimal_places1, decimal_places2)
    num1 *= 10 ** max_decimal_places
    num2 *= 10 ** max_decimal_places

    # 小数点以下の桁数が同じになるように調整
    result = soroban_addition(int(num1), int(num2))
    return result / (10 ** max_decimal_places)

def soroban_decimal_subtraction(num1, num2):
    # 文字列として扱い、小数点以下の桁数を揃える
    str_num1, str_num2 = str(num1), str(num2)
    decimal_places1 = str_num1[::-1].find('.') if '.' in str_num1 else 0
    decimal_places2 = str_num2[::-1].find('.') if '.' in str_num2 else 0
    max_decimal_places = max(decimal_places1, decimal_places2)
    num1 *= 10 ** max_decimal_places
    num2 *= 10 ** max_decimal_places

    # 小数点以下の桁数が同じになるように調整
    result = soroban_subtraction(int(num1), int(num2))
    return result / (10 ** max_decimal_places)

# 使用例
num1 = 123.45
num2 = 67.89
result_add = soroban_decimal_addition(num1, num2)
result_sub = soroban_decimal_subtraction(num1, num2)
print(f"{num1} + {num2} = {result_add}")
print(f"{num1} - {num2} = {result_sub}")

from fractions import Fraction

def soroban_fraction_addition(num1, num2):
    fraction1 = Fraction(num1)
    fraction2 = Fraction(num2)
    result = soroban_decimal_addition(fraction1.numerator, fraction2.numerator)
    return Fraction(result, 1) + Fraction(fraction1.denominator, 1)

def soroban_fraction_subtraction(num1, num2):
    fraction1 = Fraction(num1)
    fraction2 = Fraction(num2)
    result = soroban_decimal_subtraction(fraction1.numerator, fraction2.numerator)
    return Fraction(result, 1) - Fraction(fraction1.denominator, 1)

# 使用例
num1 = Fraction(3, 4)
num2 = Fraction(1, 2)
result_add = soroban_fraction_addition(num1, num2)
result_sub = soroban_fraction_subtraction(num1, num2)
print(f"{num1} + {num2} = {result_add}")
print(f"{num1} - {num2} = {result_sub}")

