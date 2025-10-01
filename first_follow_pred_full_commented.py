#!/usr/bin/env python3
# first_follow_pred_full_commented.py
# Implementación de FIRST, FOLLOW y PREDICCIÓN para gramáticas libres de contexto.
# Archivo generado y comentado línea a línea por ChatGPT para que puedas entender cada paso.
#
# Notas sobre estilo:
# - Las funciones principales usan recursión con memoización para FIRST (según tu preferencia por recursividad).
# - FOLLOW se calcula por punto fijo (iterativo) porque es más directo y evita complicar la recursión innecesariamente.
# - Los comentarios explican la intención y la lógica de cada bloque y las líneas más importantes.

from typing import Dict, List, Set, Tuple

# ---------------------------------------------------------------------------
# Utilidad: reconocer si un símbolo es un no terminal.
# Aquí definimos nuestra convención: un no terminal es una cadena formada solo por
# letras y en mayúsculas (por ejemplo, 'S', 'A', 'B').
# ---------------------------------------------------------------------------
def is_nonterminal(sym: str) -> bool:
    # Verificamos que sym sea una cadena y que consista de letras y esté en mayúsculas.
    # Esto separa automáticamente terminales como 'a', 'dos', 'uno' (no serán mayúsculas)
    return isinstance(sym, str) and sym.isalpha() and sym.isupper()

# ---------------------------------------------------------------------------
# Clase Grammar: encapsula una gramática y ofrece métodos FIRST, FIRST(rhs),
# FOLLOW_ALL y prediction_sets.
# ---------------------------------------------------------------------------
class Grammar:
    def __init__(self, productions: Dict[str, List[List[str]]], start: str):
        # productions: diccionario donde la clave es un no terminal 'A' y el valor
        # es una lista de rhs; cada rhs es una lista de símbolos (terminales o no terminales).
        # start: símbolo inicial (por ejemplo 'S').
        self.productions = productions
        self.start = start

        # Cachés para memoización (evitan recomputar y evitan bucles infinitos):
        # _first_cache guarda FIRST(X) para cada no terminal X.
        # _first_rhs_cache guarda FIRST(alpha) para secuencias alpha (tuplas).
        # _nullable_cache podría usarse para marcar si una rhs deriva ε (lo inferimos desde FIRST(rhs)).
        # _follow_cache acumula FOLLOW(X) durante la iteración.
        self._first_cache: Dict[str, Set[str]] = {}
        self._first_rhs_cache: Dict[Tuple[str, ...], Set[str]] = {}
        self._nullable_cache: Dict[Tuple[str, ...], bool] = {}
        self._follow_cache: Dict[str, Set[str]] = {}

    # ----------------------------- FIRST(X) ---------------------------------
    # Calcula FIRST de un no terminal X (con memoización).
    # La implementación es recursiva porque FIRST(X) puede depender de FIRST de otros no terminales.
    # ------------------------------------------------------------------------
    def first(self, X: str) -> Set[str]:
        # Si ya lo calculamos, lo devolvemos de inmediato.
        if X in self._first_cache:
            return self._first_cache[X]

        # Resultado que construiremos gradualmente.
        result: Set[str] = set()

        # Guardamos una referencia temprana en la caché para prevenir recursión infinita
        # en el caso de gramáticas con recursión izquierda (por ejemplo X -> X a).
        # Al colocar un set vacío, si durante la recursión volvemos a pedir FIRST(X),
        # obtendremos ese set temporal y no entraremos en bucle infinito.
        self._first_cache[X] = result

        # Iteramos sobre todas las producciones X -> alpha
        for alpha in self.productions.get(X, []):
            # Calculamos FIRST(alpha) (FIRST de la secuencia derecha)
            first_alpha = self.first_of_rhs(tuple(alpha))
            # Añadimos todos los símbolos de FIRST(alpha) excepto ε
            result.update(x for x in first_alpha if x != 'ε')
            # Si FIRST(alpha) contiene ε, entonces X puede derivar ε
            if 'ε' in first_alpha:
                result.add('ε')

        # Guardamos el resultado final en la caché y lo devolvemos
        self._first_cache[X] = result
        return result

    # ------------------------- FIRST de una secuencia ------------------------
    # Calcula FIRST(alpha) donde alpha es una tupla de símbolos (terminales/no terminales).
    # Se aplica la regla estándar: iterar de izquierda a derecha, añadir FIRST(si) menos ε,
    # si FIRST(si) contiene ε, continuar; si todos contienen ε, incluir ε.
    # ------------------------------------------------------------------------
    def first_of_rhs(self, rhs: Tuple[str, ...]) -> Set[str]:
        # Si ya calculamos FIRST(rhs) antes, devolvemos la caché.
        if rhs in self._first_rhs_cache:
            return self._first_rhs_cache[rhs]

        result: Set[str] = set()

        # Caso base: rhs vacío => deriva ε
        if len(rhs) == 0:
            result.add('ε')
            self._first_rhs_cache[rhs] = result
            return result

        # Recorremos los símbolos de left a right
        for sym in rhs:
            # Si sym es terminal (no es un no terminal según nuestra convención),
            # entonces FIRST(rhs) contiene directamente ese terminal y se detiene.
            if not is_nonterminal(sym):
                result.add(sym)
                break

            # Si sym es no terminal, añadimos FIRST(sym) excepto ε
            first_sym = self.first(sym)
            result.update(x for x in first_sym if x != 'ε')

            # Si FIRST(sym) contiene ε, entonces hay que seguir al siguiente símbolo
            # porque el prefijo actual puede desaparecer. Si no contiene ε, rompemos.
            if 'ε' in first_sym:
                # continue -> seguir con el siguiente símbolo
                continue
            else:
                # sym no es nullable, ya sabemos el prefijo, rompemos.
                break
        else:
            # Este 'else' del for se ejecuta cuando el bucle no se rompió:
            # significa que todos los símbolos fueron nullable => ε está en FIRST(rhs)
            result.add('ε')

        # Guardamos en caché y devolvemos
        self._first_rhs_cache[rhs] = result
        return result

    # --------------------------- derives_epsilon -----------------------------
    # Determina si una secuencia rhs puede derivar la cadena vacía ε.
    # Se basa en FIRST(rhs): si ε ∈ FIRST(rhs), entonces rhs deriva ε.
    # ------------------------------------------------------------------------
    def derives_epsilon(self, rhs: Tuple[str, ...]) -> bool:
        return 'ε' in self.first_of_rhs(rhs)

    # ----------------------------- FOLLOW ----------------------------------
    # Calcula FOLLOW para todos los no terminales usando un algoritmo de punto fijo.
    # Inicialmente FOLLOW(start) contiene $ y repetimos propagaciones hasta que no cambie.
    # ------------------------------------------------------------------------
    def follow_all(self) -> Dict[str, Set[str]]:
        # Aseguramos que exista una entrada en el caché para cada no terminal
        for nt in self.productions.keys():
            self._follow_cache.setdefault(nt, set())

        # El símbolo final $ pertenece a FOLLOW(start)
        self._follow_cache[self.start].add('$')

        # Repetimos hasta estabilidad (fixed-point)
        changed = True
        while changed:
            changed = False
            # Recorremos cada producción A -> alpha
            for A, rhss in self.productions.items():
                for rhs in rhss:
                    symbols = rhs
                    # Recorremos los símbolos de alpha para propagar información hacia la derecha
                    for i, B in enumerate(symbols):
                        # Solo nos interesan los no terminales B
                        if not is_nonterminal(B):
                            continue

                        # Calculamos "resto" = símbolos a la derecha de B en la misma producción
                        rest = tuple(symbols[i+1:])

                        # FIRST(rest) nos indica qué terminales pueden aparecer justo después de B
                        first_rest = self.first_of_rhs(rest)

                        # Guardamos el estado anterior para detectar cambios
                        before = set(self._follow_cache[B])

                        # Añadimos FIRST(rest) sin ε a FOLLOW(B)
                        self._follow_cache[B].update(x for x in first_rest if x != 'ε')

                        # Si rest deriva ε (o rest está vacío), entonces todo FOLLOW(A) debe añadirse a FOLLOW(B)
                        if 'ε' in first_rest or len(rest) == 0:
                            self._follow_cache[B].update(self._follow_cache[A])

                        # Si FOLLOW(B) cambió, marcamos changed=True para otra iteración
                        if self._follow_cache[B] != before:
                            changed = True

        # Devolvemos el diccionario FOLLOW completo
        return self._follow_cache

    # ------------------------ Prediction sets --------------------------------
    # Para cada producción A -> alpha, PRED(A -> alpha) = FIRST(alpha) - {ε} U (si ε ∈ FIRST(alpha) entonces FOLLOW(A))
    # ------------------------------------------------------------------------
    def prediction_sets(self) -> Dict[str, Set[str]]:
        preds = {}
        # Aseguramos tener FOLLOW para todas las entradas (se calcula internamente)
        follow_all = self.follow_all()

        # Recorremos todas las producciones para formar las claves y sus conjuntos PRED
        for A, rhss in self.productions.items():
            for rhs in rhss:
                # Definimos una clave legible para la producción
                key = f"{A} -> {' '.join(rhs) if rhs else 'ε'}"
                # Calculamos FIRST(rhs)
                first_rhs = self.first_of_rhs(tuple(rhs))
                # PRED inicia con FIRST(rhs) menos ε
                pred = set(x for x in first_rhs if x != 'ε')
                # Si FIRST(rhs) contiene ε, añadimos FOLLOW(A)
                if 'ε' in first_rhs:
                    pred.update(follow_all[A])
                preds[key] = pred
        return preds

# ----------------------------- Helpers -------------------------------------
# Función auxiliar para imprimir resultados de forma legible en consola.
def pretty_print_results(title: str, productions: Dict[str, List[List[str]]], FIRST: Dict[str, Set[str]], FOLLOW: Dict[str, Set[str]], PRED: Dict[str, Set[str]]):
    print('='*60)
    print(title)
    print('-'*60)
    print('Producciones:')
    for A, rhss in productions.items():
        for rhs in rhss:
            print(f'  {A} -> {" ".join(rhs) if rhs else "ε"}')
    print('\\nFIRST:')
    for nt in sorted(FIRST.keys()):
        print(f'  FIRST({nt}) = {sorted(list(FIRST[nt]))}')
    print('\\nFOLLOW:')
    for nt in sorted(FOLLOW.keys()):
        print(f'  FOLLOW({nt}) = {sorted(list(FOLLOW[nt]))}')
    print('\\nPREDICTION sets:')
    for prod in sorted(PRED.keys()):
        print(f'  {prod} -> {sorted(list(PRED[prod]))}')
    print('='*60 + '\\n')

# ------------------------------ Ejemplo de uso ------------------------------
if __name__ == '__main__':
    # Definimos las gramáticas tal como en la presentación 6 (las dos que usamos antes).
    productions1 = {
        'S': [['A','uno','B','C'], ['S','dos']],
        'A': [['B','C','D'], ['A','tres'], ['ε']],
        'B': [['D','cuatro','C','tres']],
        'C': [['cinco','D','B'], ['ε']],
        'D': [['ε']]
    }

    # Creamos la instancia Grammar para la primera gramática, indicando 'S' como símbolo inicial
    G1 = Grammar(productions1, start='S')
    # Calculamos FIRST para cada no terminal (esto usa la implementación recursiva)
    FIRST1 = {nt: G1.first(nt) for nt in productions1.keys()}
    # Calculamos FOLLOW para todos los no terminales
    FOLLOW1 = G1.follow_all()
    # Calculamos los conjuntos de PREDICCIÓN para cada producción
    PRED1 = G1.prediction_sets()

    # Mostramos resultados en consola con formato legible
    pretty_print_results('Ejercicio 1', productions1, FIRST1, FOLLOW1, PRED1)

    # --- Segunda gramática (Ejercicio 2) ---
    productions2 = {
        'S': [['A','B','uno']],
        'A': [['dos','B'], ['ε']],
        'B': [['C','D'], ['tres']],
        'C': [['cuatro','A','B'], ['cinco']],
        'D': [['seis'], ['ε']]
    }

    G2 = Grammar(productions2, start='S')
    FIRST2 = {nt: G2.first(nt) for nt in productions2.keys()}
    FOLLOW2 = G2.follow_all()
    PRED2 = G2.prediction_sets()

    pretty_print_results('Ejercicio 2', productions2, FIRST2, FOLLOW2, PRED2)

    # Guardamos resultados en JSON para inspección fuera del script si se desea
    try:
        import json
        out = {
            'exercise1': {'productions': productions1, 'FIRST': {k: sorted(list(v)) for k,v in FIRST1.items()}, 'FOLLOW': {k: sorted(list(v)) for k,v in FOLLOW1.items()}, 'PRED': {k: sorted(list(v)) for k,v in PRED1.items()}},
            'exercise2': {'productions': productions2, 'FIRST': {k: sorted(list(v)) for k,v in FIRST2.items()}, 'FOLLOW': {k: sorted(list(v)) for k,v in FOLLOW2.items()}, 'PRED': {k: sorted(list(v)) for k,v in PRED2.items()}}
        }
        Path('/mnt/data/first_follow_pred_results_commented.json').write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
        print('Resultados guardados en /mnt/data/first_follow_pred_results_commented.json')
    except Exception as e:
        print('No se pudieron guardar los resultados en JSON:', e)
