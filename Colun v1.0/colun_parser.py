# colun_parser.py - Парсер языка Colun
import sys
from program import program_agent

def parse_colun_line(line):
    """Разбирает одну строку Colun и выполняет её."""
    line = line.strip()
    if not line or line.startswith("!"):
        return
    
    if line.endswith(';'):
        line = line[:-1]
    
    # Сначала проверяем if
    if line.startswith("Program if "):
        rest = line[len("Program "):].strip()
        condition_and_command = rest[len("if "):].strip()
        program_agent.execute("if", condition_and_command)
        return
    
    # Потом проверяем присваивание
    if program_agent._assign_value(line + ';'):
        return
    
    if not line.startswith("Program "):
        print(f"Синтаксическая ошибка: '{line}'")
        return
    
    rest = line[len("Program "):].strip()
    
    if rest.startswith("create value: "):
        name = rest[len("create value: "):].strip()
        program_agent.execute("create", "value:", name)
    
    elif rest.startswith("Calculate "):
        expr = rest[len("Calculate "):].strip()
        program_agent.execute("Calculate", expr)
    
    elif rest.startswith("Print "):
        expr = rest[len("Print "):].strip()
        program_agent.execute("Print", expr)
    
    elif rest.startswith("Loop "):
        params = rest[len("Loop "):].strip()
        program_agent.execute("Loop", params)
    
    elif rest.startswith("Ask "):
        params = rest[len("Ask "):].strip()
        program_agent.execute("Ask", params)
    
    elif rest == "Stop":
        program_agent.execute("Stop")
    
    elif rest.startswith("call function: "):
        func_name = rest[len("call function: "):].strip()
        program_agent.execute("call", "function:", func_name)
    
    elif rest == "Start":
        program_agent.execute("Start")
    
    elif rest == "End":
        program_agent.execute("End")
    
    else:
        print(f"Неизвестная команда: {rest}")

def run_colun_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    parse_colun_line(line)
                except Exception as e:
                    print(f"Ошибка в строке {line_num}: {e}")
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python colun_parser.py ваш_файл.colun")
    else:
        run_colun_file(sys.argv[1])
