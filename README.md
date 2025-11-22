# Simulador Mercedes W12 – Computação Gráfica (PyOpenGL + Pygame)

Este projeto implementa, em Python, uma representação estilizada da Mercedes W12 (temporada 2021) utilizando **PyOpenGL** para a renderização 3D e **Pygame** para criação da janela, loop de jogo e captura de eventos de teclado/mouse.

O cenário inclui:

- Pista “infinita” ao longo do eixo Z, com faixas, bordas e gramado;
- Carro em escala aproximada de Fórmula 1 (comprimento, largura, entre-eixos);
- Modelagem por blocos (primitivas box/cylinder) para:
  - Chassi, monocoque e cockpit;
  - Nariz fino entre suspensão e asa dianteira;
  - Asa dianteira multi-elemento com detalhes em PETRONAS;
  - Asa traseira com DRS funcional;
  - Assoalho em camadas com plank, piso lateral e difusor;
  - Sidepods com undercut;
  - Halo, airbox (INEOS) e shark fin;
  - Rodas e suspensão com hastes em “V”.

---

## Controles

**Teclado**

- `ESC` → Fecha o simulador.
- `SPACE` → Inicia/pausa a animação:
  - Primeiro `SPACE`: carro começa a acelerar.
  - Outro `SPACE`: pausa a animação e o carro é “freado” (speed = 0).
- `↑ (seta para cima)` → Aceleração manual extra enquanto a animação estiver ativa.
- `↓ (seta para baixo)` → Freio manual (reduz a velocidade mais rapidamente).
- `←` → Gira levemente o carro para a esquerda (rotação visual do modelo em torno do eixo Y).
- `→` → Gira levemente o carro para a direita.
- `D` → Alterna o **DRS** (abre/fecha o flap da asa traseira).

**Mouse**

- **Movimento do mouse** (com foco na janela):
  - Rotaciona a câmera ao redor do carro (orbital):
    - Eixo X do mouse → yaw (rotação lateral);
    - Eixo Y do mouse → pitch (ângulo vertical).
- **Scroll do mouse**:
  - Aproxima/afasta a câmera (zoom), limitado por uma distância mínima e máxima.

A câmera sempre segue o carro ao longo do eixo Z, mas o usuário é livre para orbitar e ajustar o zoom, sem que a câmera atravesse a pista (altura mínima é mantida acima do solo).

---

## Lógica geral de funcionamento

### Loop principal (`main()`)

- Inicializa o Pygame, cria a janela OpenGL (modo `RESIZABLE`) e chama `init_opengl`.
- Controla o **game loop** (while `running`), tratando:
  - Eventos de janela (`QUIT`, `VIDEORESIZE`);
  - Teclado (`KEYDOWN` para ESC, SPACE, D);
  - Mouse (`MOUSEWHEEL` para zoom);
  - Captura de teclas pressionadas continuamente (`pygame.key.get_pressed`).

No loop, são atualizados:

- `car_speed` → velocidade do carro (com aceleração, frenagem e limite);
- `travel_distance` e `car_z` → posição do carro na pista;
- `wheel_angle` → rotação das rodas, calculada pela distância percorrida e circunferência;
- `camera_yaw`, `camera_pitch`, `camera_distance` → parâmetros da câmera orbital;
- Flag `drs_open` → controla abertura do flap da asa traseira;
- Flag `animation_running` / `animation_finished` → fluxo da animação.

Ao final de cada frame:

1. É montada a câmera com `gluLookAt`, apontando para a posição do carro.
2. São desenhados:
   - Pista (`draw_track()`),
   - Carro (`draw_car()`), transladado para `car_z` e rotacionado pelo `steer_angle`.

---

## Principais funções de desenho

### Primitivas

- `draw_box(width, height, depth)`  
  Desenha um paralelepípedo centrado na origem, usando um cubo unitário escalado. É a base para quase todas as partes do carro (chassi, asas, sidepods, etc.).

- `draw_cylinder(radius, length, segments)`  
  Desenha um cilindro com eixo ao longo de X (usado para as rodas/pneus).

### Pista

- `draw_track()`  
  Cria uma pista longa no eixo Z com:
  - Gramado;
  - Faixa de asfalto;
  - Bordas brancas laterais;
  - Faixa central tracejada.

As diferentes alturas em Y evitam problemas de z-fighting na renderização.

### Assoalho

- `draw_floor()`  
  Modela o piso da F1 em camadas:
  - **Plank central** (madeira/marrom);
  - Regiões de piso lateral (frontal, central e traseira) com larguras diferentes, simulando o recorte do regulamento;
  - **Difusor traseiro** inclinado;
  - Bordas em PETRONAS na região central.

### Asa dianteira

- `draw_front_wing()`  
  Constrói a asa dianteira com:
  - Plano principal preto;
  - Flaps teal em múltiplos elementos com recortes (“vasado”), simulados por sobreposição de caixas pretas;
  - Pequenos **canards** centrais;
  - Endplates pretos com detalhe teal.

### Suspensão

- `draw_wishbone(p_inner, p_outer, y, ...)`  
  Desenha uma haste de suspensão ligando um ponto interno no chassi a um ponto externo próximo à roda, na altura `y`.

Dentro de `draw_car()` são chamadas várias `draw_wishbone` para formar as hastes em “V” na suspensão dianteira e traseira.

### Carro completo

- `draw_car(wheel_angle, drs_open)`  
  Combina todos os elementos:

  - Assoalho (`draw_floor()`);
  - Chassi traseiro e monocoque dianteiro;
  - Nariz fino (dividido em trecho intermediário e ponta, entre suspensão e asa);
  - Cockpit, faixas prateadas, halo, airbox e shark fin;
  - Sidepods com undercut e detalhes PETRONAS;
  - Asa dianteira (`draw_front_wing()`);
  - Asa traseira com DRS (aberto/fechado via `drs_open`);
  - Rodas (quatro cilindros, com rotação em função de `wheel_angle`);
  - Suspensão com hastes em V (`draw_wishbone` em cada canto do carro).

---

## Inicialização do OpenGL

- `init_opengl(width, height)`  
  Configura o viewport, projeção em perspectiva (`gluPerspective`) com plano próximo em 1.0 e plano distante em 5000.0, ativa o depth test e define a cor de fundo.
