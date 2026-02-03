# program.py - Ядро языка Colun
import re

class Program:
    def __init__(self):
        self.variables = {}
        self.last_calculation = None
        self.functions = {
            "Print": self._function_print,
            "Calculate": self._function_calculate,
            "Loop": self._function_loop,
            "Stop": self._function_stop,
            "Ask": self._function_ask
        }
        self.should_stop = False
        self.is_looping = False
    
    # ==================== ОСНОВНЫЕ МЕТОДЫ ====================
    def execute(self, action, *args):
        method_name = f"cmd_{action}"
        if hasattr(self, method_name):
            getattr(self, method_name)(*args)
        else:
            print(f"Ошибка: Программа не знает команду '{action}'")
    
    # ==================== ЯДРО ПРОГРАММЫ ====================
    def cmd_Start(self):
        print(">> Программа начинает работу...")
    
    def cmd_End(self):
        print(">> Программа завершена.")
        exit(0)
    
    # ==================== ПЕРЕМЕННЫЕ ====================
    def cmd_create(self, _, name):
        """Program create value: A;"""
        if name in self.variables:
            print(f">> Переменная '{name}' уже существует")
        else:
            self.variables[name] = None
            print(f">> Создана переменная '{name}'")
    
    def _assign_value(self, line):
        """Обработка строки вида 'A = 5;'"""
        if '=' not in line:
            return False
        
        name, value = line.split('=', 1)
        name = name.strip()
        value = value.strip().rstrip(';')
        
        if name not in self.variables:
            print(f"ОШИБКА: Переменная '{name}' не создана. Сначала: Program create value: {name};")
            return True
        
        try:
            if '.' in value:
                self.variables[name] = float(value)
            else:
                self.variables[name] = int(value)
        except ValueError:
            self.variables[name] = value
        
        print(f">> {name} = {self.variables[name]}")
        return True
    
    # ==================== ВЫЧИСЛЕНИЯ ====================
    def _evaluate_expression(self, expr):
        """Вычисляет арифметические выражения: A + B * C"""
        expr = expr.rstrip(';')
        
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|\d+\.?\d*|[+\-*/]', expr)
        
        values = []
        operators = []
        
        for token in tokens:
            if token in '+-*/':
                operators.append(token)
            else:
                val = self._get_value_or_number(token)
                if val is None:
                    return None
                values.append(val)
        
        if len(values) != len(operators) + 1:
            print(f"ОШИБКА: Неправильное выражение '{expr}'")
            return None
        
        # Сначала * и /
        i = 0
        while i < len(operators):
            if operators[i] in '*/':
                if operators[i] == '*':
                    values[i] = values[i] * values[i+1]
                else:
                    if values[i+1] == 0:
                        print("ОШИБКА: Деление на ноль!")
                        return None
                    values[i] = values[i] / values[i+1]
                values.pop(i+1)
                operators.pop(i)
            else:
                i += 1
        
        # Потом + и -
        result = values[0]
        for i, op in enumerate(operators):
            if op == '+':
                result += values[i+1]
            else:
                result -= values[i+1]
        
        return result
    
    # ==================== УСЛОВИЯ (if) ====================
    def _evaluate_condition(self, condition):
        """Вычисляет условие с and/or: 'x = 5 and y > 3'"""
        if ' and ' in condition:
            left, right = condition.split(' and ', 1)
            left_val = self._evaluate_simple_condition(left.strip())
            right_val = self._evaluate_simple_condition(right.strip())
            if left_val is None or right_val is None:
                return None
            return left_val and right_val
        
        if ' or ' in condition:
            left, right = condition.split(' or ', 1)
            left_val = self._evaluate_simple_condition(left.strip())
            right_val = self._evaluate_simple_condition(right.strip())
            if left_val is None or right_val is None:
                return None
            return left_val or right_val
        
        return self._evaluate_simple_condition(condition)
    
    def _evaluate_simple_condition(self, condition):
        """Вычисляет простое условие без and/or"""
        operators = ['>=', '<=', '!=', '>', '<', '=']
        
        for op in operators:
            if op in condition:
                left, right = condition.split(op)
                left = left.strip()
                right = right.strip()
                
                left_val = self._get_value_or_string(left)
                right_val = self._get_value_or_string(right)
                
                if left_val is None or right_val is None:
                    return None
                
                # Для строк
                if isinstance(left_val, str) or isinstance(right_val, str):
                    if op in ['>', '<', '>=', '<=']:
                        print(f"ОШИБКА: Нельзя сравнивать строки с '{op}'")
                        return None
                    left_val = str(left_val)
                    right_val = str(right_val)
                
                if op == '>': return left_val > right_val
                if op == '<': return left_val < right_val
                if op == '>=': return left_val >= right_val
                if op == '<=': return left_val <= right_val
                if op == '=': return left_val == right_val
                if op == '!=': return left_val != right_val
        
        print(f"ОШИБКА: Неизвестное условие '{condition}'")
        return None
    
    # ==================== ВСПОМОГАТЕЛЬНЫЕ ====================
    def _get_value_or_number(self, token):
        """Возвращает число или значение переменной"""
        if token.replace('.', '', 1).isdigit():
            if '.' in token:
                return float(token)
            else:
                return int(token)
        
        if token not in self.variables:
            print(f"ОШИБКА: Переменная '{token}' не существует")
            return None
        
        if self.variables[token] is None:
            print(f"ОШИБКА: Переменная '{token}' не имеет значения")
            return None
        
        return self.variables[token]
    
    def _get_value_or_string(self, token):
        """Возвращает число, строку или значение переменной"""
        if (token.startswith('"') and token.endswith('"')) or \
           (token.startswith("'") and token.endswith("'")):
            return token[1:-1]
        
        if token.replace('.', '', 1).isdigit():
            if '.' in token:
                return float(token)
            else:
                return int(token)
        
        if token not in self.variables:
            print(f"ОШИБКА: Переменная '{token}' не существует")
            return None
        
        if self.variables[token] is None:
            print(f"ОШИБКА: Переменная '{token}' не имеет значения")
            return None
        
        return self.variables[token]
    
    # ==================== КОМАНДЫ ====================
    def cmd_Calculate(self, expr):
        """Program Calculate A + B;"""
        result = self._evaluate_expression(expr)
        if result is not None:
            self.last_calculation = result
            print(f">> Вычислено: {expr} = {result}")
    
    def cmd_Print(self, expr):
        """Program Print "текст"; или Program Print "текст", переменная;"""
        if ',' in expr:
            text_part, var_part = expr.split(',', 1)
            text_part = text_part.strip()
            var_part = var_part.strip().rstrip(';')
            
            if (text_part.startswith('"') and text_part.endswith('"')) or \
               (text_part.startswith("'") and text_part.endswith("'")):
                text = text_part[1:-1]
            else:
                print(f"ОШИБКА: '{text_part}' не текст в кавычках")
                return
            
            if var_part in self.variables:
                var_value = self._get_variable_value(var_part)
                if var_value is not None:
                    print(text, var_value)
            else:
                result = self._evaluate_expression(var_part)
                if result is not None:
                    print(text, result)
                else:
                    print(f"ОШИБКА: '{var_part}' не распознано")
        else:
            if (expr.startswith('"') and expr.endswith('"')) or \
               (expr.startswith("'") and expr.endswith("'")):
                print(expr[1:-1])
                return
            
            if expr in self.variables:
                value = self._get_variable_value(expr)
                if value is not None:
                    print(value)
                return
            
            result = self._evaluate_expression(expr)
            if result is not None:
                print(result)
    
    def cmd_if(self, condition_and_command):
        """Program if условие then команда;"""
        if ' then ' not in condition_and_command:
            print("ОШИБКА: Неправильный формат if. Должно быть: if УСЛОВИЕ then КОМАНДА")
            return
        
        condition_str, command = condition_and_command.split(' then ', 1)
        command = command.rstrip(';')
        
        result = self._evaluate_condition(condition_str)
        if result is None:
            return
        
        if result:
            if command.startswith('Print '):
                self.cmd_Print(command[6:])
            elif command.startswith('Calculate '):
                self.cmd_Calculate(command[10:])
            elif command.startswith('Loop '):
                self.cmd_Loop(command[5:])
            else:
                print(f"ОШИБКА: Неизвестная команда в then: {command}")
    
    def cmd_Loop(self, params):
        """Program Loop "Текст", 5; или Program Loop 2+2, 3;"""
        if self.should_stop:
            return
        
        if ',' not in params:
            content = params.rstrip(';')
            count = None
        else:
            content, count_str = params.rsplit(',', 1)
            content = content.strip()
            count_str = count_str.strip().rstrip(';')
            try:
                count = int(count_str)
            except ValueError:
                print(f"ОШИБКА: '{count_str}' не число")
                return
        
        if (content.startswith('"') and content.endswith('"')) or \
           (content.startswith("'") and content.endswith("'")):
            to_print = content[1:-1]
        else:
            result = self._evaluate_expression(content)
            if result is None:
                return
            to_print = str(result)
        
        if count is None:
            self.is_looping = True
            while self.is_looping and not self.should_stop:
                print(to_print)
            self.is_looping = False
        else:
            for i in range(count):
                if self.should_stop:
                    break
                print(to_print)
    
    def cmd_Stop(self):
        """Program Stop;"""
        self.should_stop = True
        self.is_looping = False
        print(">> Цикл остановлен")
    
    def cmd_Ask(self, question_and_var):
        """Program Ask "Вопрос?", переменная;"""
        if '",' not in question_and_var:
            print('ОШИБКА: Формат: Ask "вопрос?", переменная;')
            return
        
        question_part, var_name = question_and_var.split('",', 1)
        question = question_part + '"'
        var_name = var_name.strip().rstrip(';')
        
        question = question[1:-1]
        
        user_input = input(question + " ")
        
        try:
            if '.' in user_input:
                self.variables[var_name] = float(user_input)
            else:
                self.variables[var_name] = int(user_input)
            print(f">> Сохранено число в '{var_name}': {self.variables[var_name]}")
        except ValueError:
            self.variables[var_name] = user_input
            print(f">> Сохранено в '{var_name}': {user_input}")
    
    # ==================== ФУНКЦИИ ====================
    def cmd_call(self, _, func_name):
        """Program call function: Print;"""
        if func_name in self.functions:
            self.functions[func_name]()
        else:
            print(f"ОШИБКА: Функция '{func_name}' не найдена")
    
    def _function_print(self):
        print(">> Вызвана функция Print")
    
    def _function_calculate(self):
        print(">> Вызвана функция Calculate")
    
    def _function_loop(self):
        print(">> Функция Loop доступна (используйте: Program Loop 'текст', число;)")
    
    def _function_stop(self):
        print(">> Функция Stop доступна (используйте: Program Stop;)")
    
    def _function_ask(self):
        print(">> Функция Ask доступна (используйте: Program Ask 'вопрос?', переменная;)")
    
    def _get_variable_value(self, name):
        """Для обратной совместимости"""
        return self._get_value_or_number(name)

program_agent = Program()
