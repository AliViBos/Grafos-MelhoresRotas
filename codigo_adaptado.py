import streamlit as st
import openrouteservice
import networkx as nx
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# Chave da sua conta OpenRouteService
API_KEY = "5b3ce3597851110001cf6248ddd13b334ea140ecb72b45f7e2393a58"
client = openrouteservice.Client(key=API_KEY)

st.set_page_config(page_title="Rotas Otimizadas com Dijkstra", layout="centered")

st.title("🚚 Rotas Otimizadas com Dijkstra e OpenRouteService")

st.markdown("""
Insira no mínimo **5 endereços completos** (rua, número, cidade, estado, país).
  
🧭 **Exemplo de endereço bem formatado:**  
`Av. Paulista, 1000, São Paulo, SP, Brasil`
""")

# Interface para inserir endereços
enderecos = []
for i in range(1, 6):
    endereco = st.text_input(f"Endereço {i}")
    if endereco:
        enderecos.append(endereco)

# Botão para adicionar mais endereços (opcional)
n_adicionais = st.number_input("Quantos endereços adicionais?", min_value=0, step=1)
for i in range(n_adicionais):
    endereco = st.text_input(f"Endereço adicional {i+6}")
    if endereco:
        enderecos.append(endereco)

# Função para obter coordenadas
def geocode(endereco):
    try:
        geocode_result = client.pelias_search(text=endereco)
        coord = geocode_result["features"][0]["geometry"]["coordinates"]
        return tuple(coord)
    except:
        return None

# Função para tempo entre dois pontos
def tempo_viagem(origem, destino):
    rota = client.directions(coordinates=[origem, destino], profile='driving-car', format='json')
    return rota['routes'][0]['summary']['duration']  # segundos

# Processar quando o usuário clica
if st.button("🔍 Calcular Rota Otimizada") and len(enderecos) >= 5:
    st.success("Calculando...")

    coords = []
    for end in enderecos:
        c = geocode(end)
        if not c:
            st.error(f"Endereço inválido ou não encontrado: {end}")
            st.stop()
        coords.append(c)

    # Construir grafo direcionado com pesos (tempo)
    G = nx.DiGraph()
    for i, origem in enumerate(coords):
        G.add_node(i, pos=origem)

    for i in range(len(coords)):
        for j in range(len(coords)):
            if i != j:
                try:
                    tempo = tempo_viagem(coords[i], coords[j])
                    G.add_edge(i, j, weight=tempo)
                except:
                    st.warning(f"Erro ao calcular tempo de {enderecos[i]} → {enderecos[j]}")
                    continue

    # Dijkstra: menor caminho de 0 ao último (seguindo ordem)
    try:
        caminho_otimo = nx.dijkstra_path(G, source=0, target=len(coords)-1, weight='weight')
        st.success(f"Menor caminho em tempo: {' ➝ '.join([enderecos[i] for i in caminho_otimo])}")
    except:
        st.error("Não foi possível calcular o caminho otimizado.")
        st.stop()

    # Criar mapa
    mapa = folium.Map(location=coords[0][::-1], zoom_start=12)
    cluster = MarkerCluster().add_to(mapa)

    # Marcar todos os pontos
    for i, coord in enumerate(coords):
        folium.Marker(location=coord[::-1], popup=f"{i+1}: {enderecos[i]}").add_to(cluster)

    # Desenhar todas as rotas possíveis (vermelho)
    for i, origem in enumerate(coords):
        for j, destino in enumerate(coords):
            if i != j:
                try:
                    rota = client.directions(coordinates=[origem, destino], profile='driving-car', format='geojson')
                    folium.PolyLine(locations=[(pt[1], pt[0]) for pt in rota['features'][0]['geometry']['coordinates']],
                                    color='red', weight=1, opacity=0.4).add_to(mapa)
                except:
                    continue

    # Desenhar rota otimizada (azul)
    for i in range(len(caminho_otimo) - 1):
        origem = coords[caminho_otimo[i]]
        destino = coords[caminho_otimo[i+1]]
        rota = client.directions(coordinates=[origem, destino], profile='driving-car', format='geojson')
        folium.PolyLine(locations=[(pt[1], pt[0]) for pt in rota['features'][0]['geometry']['coordinates']],
                        color='blue', weight=5, opacity=0.8).add_to(mapa)

    # Mostrar mapa
    st_folium(mapa, width=700, height=500)

else:
    st.info("Insira pelo menos 5 endereços para começar.")
