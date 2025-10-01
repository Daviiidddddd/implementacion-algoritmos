# FIRST / FOLLOW / PREDICCIÓN — Implementación en Python

### David Castellanos

**Descripción **  
Este repositorio contiene la implementación en Python de los algoritmos **FIRST**, **FOLLOW** y **PREDICCIÓN** para gramáticas libres de contexto. Acá se probaron con las gramáticas de la presentación 6.

**Contenido principal**  

- `first_follow_pred_full_commented.py` — El script (viene comentado con la explicación de lo q hace linea a linea 
- `first_follow_pred_results.json` — Resultados generados al ejecutar el script (FIRST, FOLLOW, PRED) para las gramáticas de prueba.  
- `first_follow_pred_results_commented.json` — Resultados guardados por la versión comentada.  


## Cómo se usa
Se instala python 3, luego se ejecuta el scrupt principal
```
python3 /mnt/data/first_follow_pred_full.py
```
Después aparece por consola los conjuntos **FIRST**, **FOLLOW** y **PREDICCIÓN** para las gramáticas incluidas. Los resultados también se guardan acá en `/mnt/data/first_follow_pred_results.json`.

## Resumen
Aca lo que sucede es que **FIRST(X)** recoge todos los terminales que pueden aparecer al inicio de cualquier cadena derivada de `X`. En la implementación usamos recursión con memoización para evitar recomputaciones y manejar recursión izquierda sin entrar en bucle infinito.

En este caso, para calcular **FIRST(alpha)** (cuando `alpha` es una secuencia de símbolos) iteramos de izquierda a derecha: si el primer símbolo es terminal, lo tomamos; entonces si es no terminal, añadimos sus FIRST menos ε y solo si ese no terminal puede derivar ε continuamos con el siguiente símbolo. Entonces aca incluimos ε en FIRST(alpha) solo cuando todos los símbolos del prefijo pueden derivar ε.

Por lo que nos damos cuenta que **FOLLOW(A)** (los símbolos que pueden seguir a `A`) se obtiene por propagación por lo q recorremos cada producción `B -> α A β`, añadimos FIRST(β) menos ε a FOLLOW(A) y, si β puede derivar ε, añadimos FOLLOW(B) a FOLLOW(A). El algoritmo se ejecuta hasta alcanzar un punto fijo.

## Entonces
Basicamente el conjunto de predicción para una producción `A -> α` es: `FIRST(α) - {ε}` U (si `ε ∈ FIRST(α)` entonces `FOLLOW(A)`). Esto es lo que usan los analizadores LL(1) para decidir qué producción aplicar según el símbolo de entrada.

## Conclusiones
- En este caso la convención para identificar no terminales es: cadenas formadas por letras en **mayúsculas** (ej.: `S`, `A`, `B`). Los terminales pueden ser palabras como `uno`, `dos`, `cinco`, etc.  
- Entonces aca se incluyen dos gramáticas de prueba (las de la presentacion 6) ya definidas dentro de los scripts para poder ejecutar y ver las salidas de los codigos.


---



<!-- SALIDAS_REALES_START -->
## Salidas reales — Ejercicio 1

### Producciones:
- S → A uno B C
- S → S dos
- A → B C D
- A → A tres
- A → ε
- B → D cuatro C tres
- C → cinco D B
- C → ε
- D → ε

### FIRST:
- FIRST(A) = { cuatro, ε }
- FIRST(B) = { cuatro }
- FIRST(C) = { cinco, ε }
- FIRST(D) = { ε }
- FIRST(S) = { cuatro, uno }

### FOLLOW:
- FOLLOW(A) = { tres, uno }
- FOLLOW(B) = { $, cinco, dos, tres, uno }
- FOLLOW(C) = { $, dos, tres, uno }
- FOLLOW(D) = { cuatro, tres, uno }
- FOLLOW(S) = { $, dos }

### PREDICCIÓN:
- A -> A tres -> { cuatro }
- A -> B C D -> { cuatro }
- A -> ε -> { tres, uno }
- B -> D cuatro C tres -> { cuatro }
- C -> cinco D B -> { cinco }
- C -> ε -> { $, dos, tres, uno }
- D -> ε -> { cuatro, tres, uno }
- S -> A uno B C -> { cuatro, uno }
- S -> S dos -> { cuatro, uno }

---

## Salidas reales — Ejercicio 2

### Producciones:
- S → A B uno
- A → dos B
- A → ε
- B → C D
- B → tres
- C → cuatro A B
- C → cinco
- D → seis
- D → ε

### FIRST:
- FIRST(A) = { dos, ε }
- FIRST(B) = { cinco, cuatro, tres }
- FIRST(C) = { cinco, cuatro }
- FIRST(D) = { seis, ε }
- FIRST(S) = { cinco, cuatro, dos, tres }

### FOLLOW:
- FOLLOW(A) = { cinco, cuatro, tres }
- FOLLOW(B) = { cinco, cuatro, seis, tres, uno }
- FOLLOW(C) = { cinco, cuatro, seis, tres, uno }
- FOLLOW(D) = { cinco, cuatro, seis, tres, uno }
- FOLLOW(S) = { $ }

### PREDICCIÓN:
- A -> dos B -> { dos }
- A -> ε -> { cinco, cuatro, tres }
- B -> C D -> { cinco, cuatro }
- B -> tres -> { tres }
- C -> cinco -> { cinco }
- C -> cuatro A B -> { cuatro }
- D -> seis -> { seis }
- D -> ε -> { cinco, cuatro, seis, tres, uno }
- S -> A B uno -> { cinco, cuatro, dos, tres }

---

FIN

<!-- SALIDAS_REALES_END -->
