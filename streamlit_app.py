import random
from typing import List

import matplotlib.pyplot as plt
import streamlit as st


def generate_swaps(n_players: int, n_cols: int, p: float = 0.3) -> List[List[bool]]:
    """n_cols 단계마다 인접 플레이어 사이에 사다리 가로줄(swap)이 있는지 표시하는 2D 배열을 반환합니다.
    swaps[c][i] 는 c번째 단계에서 i와 i+1 플레이어 사이에 가로줄이 있는지 여부입니다.
    규칙: 같은 단계에서 인접한 두 가로줄이 동시에 생기지 않도록 합니다 (겹침 방지).
    """
    swaps = [[False] * (n_players - 1) for _ in range(n_cols)]
    for c in range(n_cols):
        i = 0
        while i < n_players - 1:
            if random.random() < p:
                swaps[c][i] = True
                i += 2  # 바로 옆 간선과 겹치지 않도록 스킵
            else:
                i += 1
    return swaps


def simulate_ladder(swaps: List[List[bool]]) -> List[int]:
    """시뮬레이션: 위에서 아래로 내려가며 인덱스가 어떻게 이동하는지 반환.
    반환값 mapping 에서 mapping[top_index] = bottom_index
    """
    if not swaps:
        return []
    n_players = len(swaps[0]) + 1
    positions = list(range(n_players))
    for c in range(len(swaps)):
        for i in range(n_players - 1):
            if swaps[c][i]:
                positions[i], positions[i + 1] = positions[i + 1], positions[i]
    # positions[j] 는 j번째 수직선에 도착한 원래 인덱스
    # 우리가 원하는 건 top_index -> bottom_index 이므로 역 변환
    mapping = [0] * n_players
    for bottom_index, top_index in enumerate(positions):
        mapping[top_index] = bottom_index
    return mapping


def draw_ladder(swaps: List[List[bool]], player_names: List[str]) -> plt.Figure:
    n_cols = len(swaps)
    n_players = len(player_names)
    fig, ax = plt.subplots(figsize=(max(4, n_players), max(4, n_cols * 0.4)))

    # 수직선 그리기
    xs = list(range(n_players))
    ys_min, ys_max = 0, n_cols
    for x in xs:
        ax.plot([x, x], [ys_min, ys_max], color="black")

    # 가로줄(스왑) 그리기: 각 단계 c 에 대해 y = c + 0.5 위치에 그림
    for c in range(n_cols):
        y = c + 0.5
        for i in range(n_players - 1):
            if swaps[c][i]:
                ax.plot([i, i + 1], [y, y], color="tab:blue", linewidth=3)

    # 플레이어 이름과 아래 결과 위치 표시
    ax.set_xlim(-0.5, n_players - 0.5)
    ax.set_ylim(n_cols + 0.5, -0.5)
    ax.set_xticks(xs)
    ax.set_xticklabels(player_names)
    ax.set_yticks([])
    ax.set_frame_on(False)
    return fig


st.set_page_config(page_title="사다리타기 게임", layout="wide")

st.title("🎲 간단한 사다리타기 게임")

with st.sidebar:
    st.header("설정")
    n_players = st.slider("플레이어 수", min_value=2, max_value=8, value=4)
    n_cols = st.slider("사다리 가로 단계 수", min_value=3, max_value=30, value=10)
    p = st.slider("가로줄(스왑) 생성 확률", min_value=0.0, max_value=1.0, value=0.35)
    raw_players = st.text_area("플레이어 이름 (쉼표로 구분)", value=", ".join([chr(65 + i) for i in range(n_players)]))
    raw_prizes = st.text_area("상품/결과 이름 (쉼표로 구분)", value=", ".join([f"상품 {i+1}" for i in range(n_players)]))
    regen = st.button("새로운 사다리 생성")

# 플레이어/상품 이름 정리
def parse_names(raw: str, count: int, default_prefix: str):
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if len(parts) >= count:
        return parts[:count]
    # 부족하면 기본 이름으로 채움
    for i in range(len(parts), count):
        parts.append(f"{default_prefix}{i+1}")
    return parts


player_names = parse_names(raw_players, n_players, "P")
prize_names = parse_names(raw_prizes, n_players, "상품 ")

if "swaps" not in st.session_state or regen:
    st.session_state.swaps = generate_swaps(n_players, n_cols, p)

# UI: 사다리 표시
st.subheader("사다리 시각화")
fig = draw_ladder(st.session_state.swaps, player_names)
st.pyplot(fig)

# 시뮬레이션 결과
mapping = simulate_ladder(st.session_state.swaps)

st.subheader("결과")
cols = st.columns(2)
with cols[0]:
    st.write("**플레이어 (위)**")
    for i, name in enumerate(player_names):
        st.write(f"{i+1}. {name}")
with cols[1]:
    st.write("**도착 (아래)**")
    for i, prize in enumerate(prize_names):
        st.write(f"{i+1}. {prize}")

st.markdown("---")

st.subheader("플레이 결과 매칭")
for top_idx, bottom_idx in enumerate(mapping):
    st.write(f"{player_names[top_idx]} → {prize_names[bottom_idx]}")

st.info("'새로운 사다리 생성' 버튼을 누르면 사다리가 재생성됩니다. 사이드바에서 플레이어/상품 이름과 확률을 조절하세요.")

