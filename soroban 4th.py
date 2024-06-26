class DynamicSorobanEmulator:
    def __init__(self):
        self.positive_beads = {}  # 正のビーズをxy座標で管理
        self.negative_beads = {}  # 負のビーズをxy座標で管理

    def add_column(self):
        column = len(self.positive_beads)
        self.positive_beads[column] = []
        self.negative_beads[column] = []

    def ensure_columns(self, num_columns):
        while len(self.positive_beads) < num_columns:
            self.add_column()

    def add(self, x, y, value):
        try:
            if value >= 0:
                self.positive_beads[x].append((y, value))
            else:
                self.negative_beads[x].append((y, abs(value)))
        except KeyError:
            raise ValueError(f"指定された列 {x} が存在しません")

    def subtract(self, x, y, value):
        try:
            if value >= 0:
                if (y, value) in self.positive_beads[x]:
                    self.positive_beads[x].remove((y, value))
            else:
                if (y, abs(value)) in self.negative_beads[x]:
                    self.negative_beads[x].remove((y, abs(value)))
        except KeyError:
            raise ValueError(f"指定された列 {x} が存在しません")

    def multiply(self, x, factor):
        try:
            if factor >= 0:
                self.positive_beads[x] = [(y, value * factor) for (y, value) in self.positive_beads[x]]
                self.negative_beads[x] = [(y, value * factor) for (y, value) in self.negative_beads[x]]
            else:
                self.positive_beads[x], self.negative_beads[x] = (
                    [(y, value * abs(factor)) for (y, value) in self.negative_beads[x]],
                    [(y, value * abs(factor)) for (y, value) in self.positive_beads[x]],
                )
        except KeyError:
            raise ValueError(f"指定された列 {x} が存在しません")
        except Exception as e:
            raise ValueError(f"乗算エラー: {str(e)}")

    def divide(self, x, divisor):
        if divisor == 0:
            raise ValueError("除算エラー: ゼロで割ることはできません")
        try:
            if divisor > 0:
                self.positive_beads[x] = [(y, value / divisor) for (y, value) in self.positive_beads[x]]
                self.negative_beads[x] = [(y, value / divisor) for (y, value) in self.negative_beads[x]]
            else:
                self.positive_beads[x], self.negative_beads[x] = (
                    [(y, value / abs(divisor)) for (y, value) in self.negative_beads[x]],
                    [(y, value / abs(divisor)) for (y, value) in self.positive_beads[x]],
                )
        except KeyError:
            raise ValueError(f"指定された列 {x} が存在しません")
        except Exception as e:
            raise ValueError(f"除算エラー: {str(e)}")

    def display(self):
        try:
            print("Positive Beads:")
            for x in self.positive_beads:
                print(f"Column {x}: {self.positive_beads[x]}")
            print("Negative Beads:")
            for x in self.negative_beads:
                print(f"Column {x}: {self.negative_beads[x]}")
        except Exception as e:
            raise ValueError(f"表示エラー: {str(e)}")

    def process_linear_data(self, data):
        self.ensure_columns(len(data))
        try:
            for i, value in enumerate(data):
                self.add(i, 0, value)
        except Exception as e:
            raise ValueError(f"リニアデータ処理エラー: {str(e)}")

# 使用例
linear_data = [3, -4, 1.5, -2.5, 5.7, -6.1, 2.3, -1.8, 4.2, -3.3]

soroban = DynamicSorobanEmulator()
soroban.process_linear_data(linear_data)

# 表示
soroban.display()

# 追加の演算
soroban.multiply(0, -2)  # 0番目の列を-2倍する
soroban.divide(1, -2)  # 1番目の列を-2で割る

# 再表示
soroban.display()