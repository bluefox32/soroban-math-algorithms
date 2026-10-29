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
        # 修正(2026-10-29): multiplier は内側のループで増え続けるため、num2 の
        # 2桁目以降の部分積の位までずれていた。num2 の現在の桁の位 place を
        # 別に保持し、桁ごとに multiplier をその位から始め直す
        place = 1
        while num2:
            digit2 = num2 % 10
            num2 //= 10
            temp_result = 0
            carry = 0
            multiplier = place
            place *= 10
            
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
        # 修正(2026-10-29): 旧実装は除数を10倍するたびに count を1つ増やすだけで
        # 位と合っておらず、multiplier も 1 から //= 10 で 0 になって商が壊れて
        # いたため、位ごとの筆算として書き直した。最上位の位から、その位の
        # 除数 (num2 * place) を引ける回数が商のその桁になる。余りは切り捨て、
        # 整数の商を返す（従来の例・呼び出し側の想定に合わせた）
        if num2 == 0:
            raise ZeroDivisionError("division by zero")
        
        place = 1
        while num2 * place * 10 <= num1:
            place *= 10
        
        while place:
            quotient_digit = 0
            while num1 >= num2 * place:
                num1 = soroban_subtraction(num1, num2 * place)
                quotient_digit += 1
            result = soroban_addition(result, quotient_digit * place)
            place //= 10
    
    return result

# 修正(2026-10-29): soroban_addition / soroban_subtraction が未定義のまま
# 乗算・除算・小数処理から呼ばれていたため、soroban_arithmetic への
# 薄いラッパーとして追加した（実装は既存の桁ごとの演算をそのまま使う）
def soroban_addition(num1, num2):
    return soroban_arithmetic(num1, num2, 'addition')

def soroban_subtraction(num1, num2):
    return soroban_arithmetic(num1, num2, 'subtraction')

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
from math import gcd

# 修正(2026-10-29): 分数ヘルパーは通分せず分子同士を足し（引き）、1つ目の分母を
# 整数として加える誤った実装だったため、通分して分子を計算する形に書き直した。
# 分子の拡大は soroban の乗算、分子の加減は soroban の加減算（絶対値ベース）で行う
def _fraction_scaled_numerators(fraction1, fraction2):
    common_denominator = fraction1.denominator * fraction2.denominator // gcd(fraction1.denominator, fraction2.denominator)
    scaled1 = soroban_arithmetic(abs(fraction1.numerator), common_denominator // fraction1.denominator, 'multiplication')
    if fraction1.numerator < 0:
        scaled1 = -scaled1
    scaled2 = soroban_arithmetic(abs(fraction2.numerator), common_denominator // fraction2.denominator, 'multiplication')
    if fraction2.numerator < 0:
        scaled2 = -scaled2
    return scaled1, scaled2, common_denominator

def _soroban_signed_add(a, b):
    # soroban の加減算は非負整数前提のため、絶対値で計算して符号を付け直す
    if a >= 0 and b >= 0:
        return soroban_addition(a, b)
    if a <= 0 and b <= 0:
        return -soroban_addition(-a, -b)
    if abs(a) >= abs(b):
        return soroban_subtraction(abs(a), abs(b)) if a > 0 else -soroban_subtraction(abs(a), abs(b))
    return soroban_subtraction(abs(b), abs(a)) if b > 0 else -soroban_subtraction(abs(b), abs(a))

def soroban_fraction_addition(num1, num2):
    fraction1 = Fraction(num1)
    fraction2 = Fraction(num2)
    scaled1, scaled2, common_denominator = _fraction_scaled_numerators(fraction1, fraction2)
    return Fraction(_soroban_signed_add(scaled1, scaled2), common_denominator)

def soroban_fraction_subtraction(num1, num2):
    fraction1 = Fraction(num1)
    fraction2 = Fraction(num2)
    scaled1, scaled2, common_denominator = _fraction_scaled_numerators(fraction1, fraction2)
    return Fraction(_soroban_signed_add(scaled1, -scaled2), common_denominator)

# 使用例
num1 = Fraction(3, 4)
num2 = Fraction(1, 2)
result_add = soroban_fraction_addition(num1, num2)
result_sub = soroban_fraction_subtraction(num1, num2)
print(f"{num1} + {num2} = {result_add}")
print(f"{num1} - {num2} = {result_sub}")

