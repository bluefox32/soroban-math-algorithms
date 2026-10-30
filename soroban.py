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

# 追記・修正(2026-10-30): 小数演算を (仮数, スケール) 表現に統一し、乗算・除算を追加した。
# 数は mantissa * 10**(-scale) として扱い、演算そのものは整数のそろばん演算に帰着させる。
# スケールの決まりは次の通り:
#   加減算: 大きい方に揃える (max(n, m))
#   乗算  : 和 (n + m) —— 結果に 1/10**(n+m) が付く
#   除算  : 差 (n - m) —— 割り切れない場合があるため、商の小数桁数を decimal_places
#           引数で指定し、その桁まで求めて切り捨てる
# 旧実装の加減算は float 経由 (num *= 10**桁数 を int() で切り捨て) で、2.675 のような
# 値では仮数がずれる問題と、1e-05 のような指数表記で桁数を誤認する問題があったため、
# Decimal 経由で仮数とスケールを数える形に置き換えた。戻り値は正確な Decimal。
from decimal import Decimal

def _decimal_parts(value):
    # int / float / str / Decimal を (仮数, スケール) に分解する
    sign, digits, exponent = Decimal(str(value)).as_tuple()
    mantissa = int(''.join(map(str, digits))) if digits else 0
    if sign:
        mantissa = -mantissa
    if exponent >= 0:
        return mantissa * 10 ** exponent, 0
    return mantissa, -exponent

def _decimal_from_parts(mantissa, scale):
    # (仮数, スケール) から Decimal を組み立てる (コンテキスト精度の影響を受けない)
    sign = 1 if mantissa < 0 else 0
    digits = tuple(int(ch) for ch in str(abs(mantissa)))
    return Decimal((sign, digits, -scale))

def _decimal_signed_add(a, b):
    # soroban の加減算は非負整数前提のため、絶対値で計算して符号を付け直す
    # (分数ヘルパーの _soroban_signed_add と同じ方針)
    if a >= 0 and b >= 0:
        return soroban_addition(a, b)
    if a <= 0 and b <= 0:
        return -soroban_addition(-a, -b)
    if abs(a) >= abs(b):
        return soroban_subtraction(abs(a), abs(b)) if a > 0 else -soroban_subtraction(abs(a), abs(b))
    return soroban_subtraction(abs(b), abs(a)) if b > 0 else -soroban_subtraction(abs(b), abs(a))

def soroban_decimal_addition(num1, num2):
    mantissa1, scale1 = _decimal_parts(num1)
    mantissa2, scale2 = _decimal_parts(num2)
    scale = max(scale1, scale2)
    aligned1 = mantissa1 * 10 ** (scale - scale1)
    aligned2 = mantissa2 * 10 ** (scale - scale2)
    return _decimal_from_parts(_decimal_signed_add(aligned1, aligned2), scale)

def soroban_decimal_subtraction(num1, num2):
    mantissa1, scale1 = _decimal_parts(num1)
    mantissa2, scale2 = _decimal_parts(num2)
    scale = max(scale1, scale2)
    aligned1 = mantissa1 * 10 ** (scale - scale1)
    aligned2 = mantissa2 * 10 ** (scale - scale2)
    return _decimal_from_parts(_decimal_signed_add(aligned1, -aligned2), scale)

def soroban_decimal_multiplication(num1, num2):
    mantissa1, scale1 = _decimal_parts(num1)
    mantissa2, scale2 = _decimal_parts(num2)
    result = soroban_arithmetic(abs(mantissa1), abs(mantissa2), 'multiplication')
    if (mantissa1 < 0) != (mantissa2 < 0):
        result = -result
    return _decimal_from_parts(result, scale1 + scale2)

def soroban_decimal_division(num1, num2, decimal_places=10):
    mantissa1, scale1 = _decimal_parts(num1)
    mantissa2, scale2 = _decimal_parts(num2)
    if mantissa2 == 0:
        raise ZeroDivisionError("division by zero")
    # 商 = (mantissa1 / mantissa2) * 10**(scale2 - scale1)。
    # 小数 decimal_places 桁までの整数商になるよう、分子を先にスケーリングする
    shift = decimal_places + scale2 - scale1
    if shift >= 0:
        numerator = abs(mantissa1) * 10 ** shift
        denominator = abs(mantissa2)
    else:
        numerator = abs(mantissa1)
        denominator = abs(mantissa2) * 10 ** (-shift)
    quotient = soroban_arithmetic(numerator, denominator, 'division')
    if (mantissa1 < 0) != (mantissa2 < 0):
        quotient = -quotient
    return _decimal_from_parts(quotient, decimal_places)

# 使用例
num1 = 123.45
num2 = 67.89
result_add = soroban_decimal_addition(num1, num2)
result_sub = soroban_decimal_subtraction(num1, num2)
result_mul = soroban_decimal_multiplication(num1, num2)
result_div = soroban_decimal_division(num1, num2)
print(f"{num1} + {num2} = {result_add}")
print(f"{num1} - {num2} = {result_sub}")
print(f"{num1} * {num2} = {result_mul}")
print(f"{num1} / {num2} = {result_div}")

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

