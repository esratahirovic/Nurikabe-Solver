import time
import numpy as np

# Nurikabe Kuralları ve Kısıtlar:
# 1. Adalar:
#    - Her adada tam olarak bir numaralandırılmış hücre bulunmalıdır.
#    - Adalar yalnızca köşe noktalarından (diyagonal) temas edebilir, yatay veya dikey birleşime izin verilmez.
# 2. Deniz:
#    - Siyah hücreler, ızgarada tek bir bağlantılı yapı oluşturmalıdır.
#    - Siyah hücreler hiçbir zaman 2x2 kare veya daha büyük bir kare oluşturamaz.
# 3. Tüm Hücreler:
#    - Her hücre ya siyah (deniz) ya da beyaz (ada) olarak atanmalıdır.
# 4. Süreklilik ve İzolasyon:
#    - Siyah hücreler tek bir bağlantılı bütün oluştururken, beyaz hücrelerin kendi rakamlarına bağlı olarak mantıklı şekilde büyütülmesi gerekir.

def create_game_board_from_single_input():
    """
    Kullanıcıdan oyun tahtası girdisini alır ve bir oyun tahtası oluşturur.
    - Kullanıcı girdisinin doğru formatta olup olmadığını kontrol eder.
    - Satırların eşit uzunlukta olup olmadığını doğrular.
    """
    print("Nurikabe oyun tahtası oluşturuluyor.")
    print("Oyun tahtasını tek bir satırda girebilirsiniz.")
    print("Satırları ',' ile, hücreleri ise boşluk ile ayırın.")
    print("\"2 NaN NaN 3, NaN NaN NaN NaN, NaN NaN NaN NaN, 4 NaN NaN NaN\"")
    print("\"NaN NaN NaN 1, 1 NaN NaN NaN, NaN NaN 2 NaN, 1 NaN NaN NaN\"")
    print("\"2 NaN NaN NaN, NaN NaN NaN NaN, NaN NaN NaN NaN , NaN 1 NaN 4\"")
    print("\"2 NaN NaN 2, NaN NaN NaN NaN, NaN NaN NaN NaN, NaN 2 NaN 1\"")
    print("\"NaN NaN NaN NaN NaN , 2 NaN 4 NaN NaN, NaN NaN NaN 2 NaN, NaN NaN NaN NaN NaN, NaN 2 NaN NaN NaN\"") 
    print("\"NaN NaN NaN NaN NaN , NaN 1 NaN 1 NaN, NaN NaN 2 NaN 3, NaN NaN NaN NaN NaN, 2 NaN NaN NaN NaN\"")

    # Kullanıcıdan veri alımı
    board_input = input("Oyun tahtasını girin: ")
    rows = board_input.split(',')
    game_board = []

    for row in rows:
        try:
            # Her hücreyi işler, boş hücreleri None olarak işaretler
            game_board.append([
                None if cell.strip().lower() == 'nan' else int(cell.strip())
                for cell in row.split()
            ])
        except ValueError:
            # Geçersiz giriş durumunda hata mesajı
            print("Hatalı bir girdi tespit edildi. Lütfen formatı kontrol edin.")
            return None

    # Satır uzunluklarının tutarlılığını kontrol eder
    if len(set(len(row) for row in game_board)) > 1:
        print("Hata: Tüm satırların aynı uzunlukta olması gerekir.")
        return None

    return np.array(game_board, dtype=object)

def start_timer():
    """
    Çözüm için geçen süreyi ölçmek için başlangıç zamanını döndürür.
    """
    return time.time()

def end_timer(start_time):
    """
    Geçen süreyi hesaplar ve döndürür.
    """
    return time.time() - start_time

def print_board(board, file=None):
    """
    Oyun tahtasını ekrana ve opsiyonel olarak dosyaya yazdırır.
    """
    for row in board:
        # Satırı yazdırmak için boş hücreleri NaN olarak işaretler
        line = " ".join(str(cell) if cell is not None else 'NaN' for cell in row)
        print(line)
        if file:
            file.write(line + '\n')
    if file:
        file.write("\n")

def initialize_domains(game_board, file=None):
    """
    Hücreler için domainleri başlatır ve numaralandırılmış hücreleri tanımlar.
    - Boş hücreler hem ada hem deniz olabilir.
    - Numaralı hücreler yalnızca belirli ada boyutlarını temsil eder.
    """
    domains = {}
    numerical_cells = []
    for x in range(game_board.shape[0]):
        for y in range(game_board.shape[1]):
            if game_board[x, y] is None:
                # Boş hücre için domain
                domains[(x, y)] = ['L', 'S']
            elif isinstance(game_board[x, y], int):
                # Numaralı hücre için domain ve ada tanımı
                domains[(x, y)] = [f'L{game_board[x, y]}']
                numerical_cells.append({'konum': (x, y), 'deger': game_board[x, y]})

    # Domain bilgilerini dosyaya yazdır
    if file:
        file.write("Başlangıç domainleri:\n")
        for cell, domain in domains.items():
            file.write(f"{cell}: {domain}\n")
        file.write("\n")

    # Sayısal hücreleri dosyaya logla
    if file:
        file.write("Numerical hücreler:\n")
        for cell in numerical_cells:
            file.write(f"{cell}\n")
        file.write("\n")

    if file:
        file.write(f"Toplam ada sayısı: {len(numerical_cells)}\n\n")

    return domains, numerical_cells

def log_step(file, message):
    """
    Her adımın açıklamasını hem ekrana hem de dosyaya yazar.
    """
    print(message)
    if file:
        file.write(message + '\n')

def update_and_log_board(variable_values, game_board, file):
    """
    Oyun tahtasını günceller ve çıktıya yazar.
    - Hücre değerlerini çözüme göre günceller.
    """
    solved_board = np.full_like(game_board, 'NaN', dtype=object)
    for (x, y), value in variable_values.items():
        # Hücreye ya oyun tahtasındaki mevcut değeri ya da çözüme göre atanmış değeri yaz
        solved_board[x, y] = game_board[x, y] if isinstance(game_board[x, y], int) else value
    log_step(file, "Güncellenen oyun tahtası:")
    print_board(solved_board, file)

def select_next_variable(domains, numerical_cells, variable_values):
    """
    MRV (Minimum Remaining Values) stratejisini uygular.
    - Öncelikle genişleme ihtiyacı olan sayısal hücrelere odaklanır.
    - Daha sonra domain boyutuna göre seçim yapar.
    """
    # İşlenmemiş sayısal hücreleri sıralar
    numerical_cells_sorted = sorted(
        [cell for cell in numerical_cells if variable_values.get(cell['konum']) is None],
        key=lambda c: (c['deger'], len(domains[c['konum']]))
    )

    if numerical_cells_sorted:
        return numerical_cells_sorted[0]['konum']

    # MRV stratejisine göre diğer hücrelerden seçim yapar
    unassigned_vars = [var for var in domains if len(domains[var]) > 1 and variable_values.get(var) is None]
    return min(unassigned_vars, key=lambda v: len(domains[v])) if unassigned_vars else None

def forward_checking(domains, variable, value, game_board, variable_values, file):
    """
    Atama sonrası forward checking uygular.
    - Komşu hücrelerin domainlerini günceller.
    - Ada boyutunun tamamlanıp tamamlanmadığını kontrol eder.
    """
    updated_domains = {k: v.copy() for k, v in domains.items()}
    updated_domains[variable] = [value]

    log_step(file, f"Forward checking uygulanıyor: {variable} = {value}")

    if value.startswith('L') and isinstance(game_board[variable[0], variable[1]], int):
        target_size = game_board[variable[0], variable[1]]
        current_size = 1
        visited = set()
        stack = [variable]

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited or not variable_values.get((cx, cy), '').startswith('L'):
                continue
            visited.add((cx, cy))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (cx + dx, cy + dy)
                if neighbor in domains and variable_values.get(neighbor, '').startswith('L'):
                    stack.append(neighbor)
                    current_size += 1

        # Ada boyutu tamamlanmışsa, çevresindeki hücreleri deniz yap
        if current_size == target_size:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (variable[0] + dx, variable[1] + dy)
                if neighbor in updated_domains:
                    updated_domains[neighbor] = ['S']

    update_and_log_board(variable_values, game_board, file)
    return updated_domains

def is_valid_assignment(variable_values, game_board):
    """
    Mevcut atamanın tüm kısıtları sağladığını doğrular.
    - 2x2 siyah kare kontrolü.
    - Siyah hücrelerin bağlantılı bütün oluşturması.
    - Ada boyutlarının doğru olması.
    """
    for (x, y), value in variable_values.items():
        if isinstance(game_board[x, y], int) and value.startswith('L'):
            target_size = game_board[x, y]
            visited = set()
            stack = [(x, y)]
            size = 0
            while stack:
                cx, cy = stack.pop()
                if (cx, cy) in visited or not variable_values.get((cx, cy), '').startswith('L'):
                    continue
                visited.add((cx, cy))
                size += 1
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    neighbor = (cx + dx, cy + dy)
                    if neighbor in variable_values:
                        stack.append(neighbor)
            if size != target_size:
                return False

    for (x, y), value in variable_values.items():
        if value.startswith('S'):
            square = [(x + dx, y + dy) for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]]
            if all(variable_values.get(cell, '').startswith('S') for cell in square):
                return False

    visited = set()
    stack = []
    for (x, y), value in variable_values.items():
        if value.startswith('S'):
            stack = [(x, y)]
            break

    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (cx + dx, cy + dy)
            if neighbor in variable_values and variable_values[neighbor].startswith('S'):
                stack.append(neighbor)

    for (x, y), value in variable_values.items():
        if value.startswith('S') and (x, y) not in visited:
            return False

    return True

def backtrack(domains, variable_values, game_board, numerical_cells, step=1, file=None):
    """
    Geriye dönük izleme algoritmasını uygular.
    - MRV ile değişken seçimi yapar.
    - Çözüme ulaşılana kadar değer atar ve kısıtları kontrol eder.
    """
    if all(len(domains[var]) == 1 for var in domains):
        if is_valid_assignment(variable_values, game_board):
            return variable_values
        return None

    selected_var = select_next_variable(domains, numerical_cells, variable_values)
    if not selected_var:
        return None

    log_step(file, f"Adım {step}: MRV seçimi {selected_var}, domain: {domains[selected_var]}")

    for value in domains[selected_var]:
        log_step(file, f"Adım {step}: {selected_var} = {value} deneniyor")

        updated_domains = forward_checking(domains, selected_var, value, game_board, variable_values, file)
        updated_values = variable_values.copy()
        updated_values[selected_var] = value

        update_and_log_board(updated_values, game_board, file)

        result = backtrack(updated_domains, updated_values, game_board, numerical_cells, step + 1, file)
        if result is not None:
            return result

    log_step(file, f"Adım {step}: {selected_var} geri alınarak backtracking yapılıyor")
    return None

def solve_nurikabe(game_board, file):
    """
    Nurikabe bulmacasını çözmek için ana fonksiyon.
    - Başlangıç domainlerini oluşturur.
    - Geriye dönük izleme algoritmasını çağırır.
    """
    domains, numerical_cells = initialize_domains(game_board, file)
    variable_values = {var: None for var in domains}
    for (x, y), value in domains.items():
        if len(value) == 1 and value[0].startswith('L') and isinstance(game_board[x, y], int):
            variable_values[(x, y)] = value[0]
    return backtrack(domains, variable_values, game_board, numerical_cells, file=file)

print("\nNurikabe Oyun Tahtasını Oluşturun:")
game_board = create_game_board_from_single_input()
if game_board is None:
    print("Oyun tahtası oluşturulamadı.")
    exit()

print("\nBaşlangıç Oyun Tahtası:")
with open("nurikabe_output.txt", "w") as output_file:
    print_board(game_board, output_file)

start_time = start_timer()
with open("nurikabe_output.txt", "a") as output_file:
    solution = solve_nurikabe(game_board, output_file)
duration = end_timer(start_time)

with open("nurikabe_output.txt", "a") as output_file:
    if solution:
        output_file.write(f"Çözüm süresi: {duration:.2f} saniye\n")
        solved_board = np.full_like(game_board, 'NaN', dtype=object)
        for (x, y), value in solution.items():
            solved_board[x, y] = game_board[x, y] if isinstance(game_board[x, y], int) else value
        output_file.write("\nÇözüm:\n")
        print_board(solved_board, output_file)
    else:
        output_file.write("Çözüm bulunamadı.\n")
