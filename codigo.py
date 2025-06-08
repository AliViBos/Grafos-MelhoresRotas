import openrouteservice
import folium

# Substitua pela sua chave de API do OpenRouteService
api_key = '5b3ce3597851110001cf6248ddd13b334ea140ecb72b45f7e2393a58'
client = openrouteservice.Client(key=api_key)

def geocodificar_endereco(endereco):
    try:
        resultado = client.pelias_search(text=endereco)
        coordenadas = resultado['features'][0]['geometry']['coordinates']
        return coordenadas  # formato: [longitude, latitude]
    except Exception as e:
        print(f"❌ Erro ao geocodificar o endereço '{endereco}': {e}")
        return None

def gerar_rota(origem, destino, perfil):
    try:
        rota = client.directions(
            coordinates=[origem, destino],
            profile=perfil,
            format='geojson'
        )
        return rota
    except Exception as e:
        print(f"❌ Erro ao gerar rota: {e}")
        return None

def criar_mapa(rota, origem, destino):
    mapa = folium.Map(location=[origem[1], origem[0]], zoom_start=13)
    folium.Marker([origem[1], origem[0]], tooltip='Origem', icon=folium.Icon(color='green')).add_to(mapa)
    folium.Marker([destino[1], destino[0]], tooltip='Destino', icon=folium.Icon(color='red')).add_to(mapa)
    folium.GeoJson(rota, name='Rota').add_to(mapa)
    mapa.save('rota.html')
    print("✅ Mapa salvo como 'rota.html'.")

def main():
    print("🧭 Bem-vindo ao gerador de rotas com OpenRouteService!\n")

    origem_input = input("Digite o endereço de origem (ex: Rua Papa Gregório Magno, 813 - Vila Missionária, São Paulo): ")
    destino_input = input("Digite o endereço de destino (ex: Rua Engenheiro Flávio da Costa, 181 - Pedreira, São Paulo): ")
    perfil = input("Digite o perfil de transporte (driving-car, driving-hgv, foot-walking): ")

    if not origem_input or not destino_input or not perfil:
        print("❌ Todos os campos são obrigatórios. Tente novamente.")
        return

    origem_coords = geocodificar_endereco(origem_input)
    destino_coords = geocodificar_endereco(destino_input)

    if not origem_coords or not destino_coords:
        print("❌ Não foi possível geocodificar um ou ambos os endereços.")
        return

    rota = gerar_rota(origem_coords, destino_coords, perfil)

    if rota:
        criar_mapa(rota, origem_coords, destino_coords)

if __name__ == '__main__':
    main()
