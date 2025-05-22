import pandas as pd
import geopandas
from shapely.geometry import Point
import folium
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, font
import webbrowser
import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

class MapaTkinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualização de Coordenadas no Mapa")

        self.style = ttk.Style(root)
        self.style.theme_use('vista')

        self.button_font = font.Font(family="Roboto", size=10)
        self.label_font = font.Font(family="Roboto", size=9)

        self.style.configure('TButton', font=self.button_font, padding=8)
        self.style.configure('TLabelFrame.Label', font=self.label_font)
        self.style.configure('TLabel', font=self.label_font)

        self.mapa_arquivo = None
        self.nome_arquivo_json = "sete_maravilhasm.json"
        self.nome_arquivo_xml = "sete_maravilhasa.xml"
        self.nome_arquivo_csv = "sete_maravilhasn.csv"
        self.coordenadas = self.carregar_coordenadas()
        self.atualizar_mapa()

        self.frame_importar = ttk.LabelFrame(root, text="Mapas disponíveis:")
        self.frame_importar.pack(padx=20, pady=20, fill="x")

        self.btn_carregar_json = ttk.Button(self.frame_importar, text="Sete Maravilhas do Mundo Moderno", command=self.carregar_e_abrir_json)
        self.btn_carregar_json.pack(pady=10, padx=10, fill="x")

        self.btn_carregar_xml = ttk.Button(self.frame_importar, text="Sete Maravilhas do Mundo Antigo", command=self.carregar_e_abrir_xml)
        self.btn_carregar_xml.pack(pady=10, padx=10, fill="x")

        self.btn_carregar_csv = ttk.Button(self.frame_importar, text="Sete Maravilhas Naturais do Mundo", command=self.carregar_e_abrir_csv)
        self.btn_carregar_csv.pack(pady=10, padx=10, fill="x")

        self.btn_mostrar_tabela = ttk.Button(root, text="Mostrar Tabela de Coordenadas", command=self.mostrar_tabela_coordenadas)
        self.btn_mostrar_tabela.pack(pady=15, padx=20, fill="x")

        self.lbl_instrucao = ttk.Label(root, text="Escolha uma das opções.")
        self.lbl_instrucao.pack(pady=15)

    def carregar_coordenadas(self):
        if os.path.exists(self.nome_arquivo_json):
            return self.importar_json_interno(self.nome_arquivo_json)
        elif os.path.exists(self.nome_arquivo_xml):
            return self.importar_xml_interno(self.nome_arquivo_xml)
        elif os.path.exists(self.nome_arquivo_csv):
            return self.importar_csv_interno(self.nome_arquivo_csv)
        return []

    def importar_json_interno(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if 'coordenadas' in data and isinstance(data['coordenadas'], list):
                    return data['coordenadas']
                else:
                    messagebox.showerror("Erro", f"Arquivo JSON '{file_path}' inválido.")
                    return []
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler arquivo JSON '{file_path}': {e}")
            return []

    def importar_xml_interno(self, file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            coordenadas = []
            for ponto in root.findall('ponto'):
                nome = ponto.find('nome').text if ponto.find('nome') is not None else ''
                latitude = float(ponto.find('latitude').text)
                longitude = float(ponto.find('longitude').text)
                coordenadas.append({'nome': nome, 'latitude': latitude, 'longitude': longitude})
            return coordenadas
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler arquivo XML '{file_path}': {e}")
            return []

    def importar_csv_interno(self, file_path):
        try:
            df = pd.read_csv(file_path)
            if 'latitude' in df.columns and 'longitude' in df.columns:
                return df.to_dict('records')
            else:
                messagebox.showerror("Erro", f"Arquivo CSV '{file_path}' inválido.")
                return []
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler arquivo CSV '{file_path}': {e}")
            return []

    def criar_mapa(self):
        if not self.coordenadas:
            messagebox.showinfo("Aviso", "Nenhuma coordenada para exibir no mapa.")
            return None

        df = pd.DataFrame(self.coordenadas)
        geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
        gdf = geopandas.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

        if not gdf.empty:
            mean_lat = gdf['latitude'].mean()
            mean_lon = gdf['longitude'].mean()
            m = folium.Map(location=[mean_lat, mean_lon], zoom_start=2)
            for index, row in gdf.iterrows():
                nome = row.get('nome', 'Sem Nome')
                latitude = row['latitude']
                longitude = row['longitude']
                folium.Marker(
                    location=[latitude, longitude],
                    popup=f"<b>{nome}:</b><br>{latitude}<br>{longitude}", icon=folium.Icon(icon = "glyphicon glyphicon-pushpin")
                ).add_to(m)
        else:
            m = folium.Map(location=[0, 0], zoom_start=2)

        map_filename = "mapa_tkinter.html"
        m.save(map_filename)
        return map_filename

    def atualizar_mapa(self):
        self.mapa_arquivo = self.criar_mapa()

    def abrir_mapa(self):
        if self.mapa_arquivo:
            webbrowser.open("file://" + os.path.abspath(self.mapa_arquivo))
        else:
            messagebox.showinfo("Aviso", "Nenhum mapa foi gerado ainda.")

    def carregar_e_abrir_json(self):
        self.coordenadas = self.importar_json_interno(self.nome_arquivo_json)
        self.atualizar_mapa()
        self.abrir_mapa()

    def carregar_e_abrir_xml(self):
        self.coordenadas = self.importar_xml_interno(self.nome_arquivo_xml)
        self.atualizar_mapa()
        self.abrir_mapa()

    def carregar_e_abrir_csv(self):
        self.coordenadas = self.importar_csv_interno(self.nome_arquivo_csv)
        self.atualizar_mapa()
        self.abrir_mapa()

    def mostrar_tabela_coordenadas(self):
        coordenadas_json = self.importar_json_interno(self.nome_arquivo_json)
        coordenadas_xml = self.importar_xml_interno(self.nome_arquivo_xml)
        coordenadas_csv = self.importar_csv_interno(self.nome_arquivo_csv)
        todas_coordenadas = coordenadas_json + coordenadas_xml + coordenadas_csv

        if not todas_coordenadas:
            messagebox.showinfo("Aviso", "Nenhuma coordenada encontrada nos arquivos.")
            return

        df = pd.DataFrame(todas_coordenadas)

        tabela_window = Toplevel(self.root)
        tabela_window.title("Tabela de Coordenadas")

        tree = ttk.Treeview(tabela_window, columns=list(df.columns), show="headings")

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        for _, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))

        tree.pack(expand=True, fill="both", padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = MapaTkinterApp(root)
    root.mainloop()
