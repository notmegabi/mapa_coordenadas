import pandas as pd
import geopandas
from shapely.geometry import Point
import folium
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

class MapaTkinterApp:
    def __init__(self, root, coordenadas_iniciais=None):
        self.root = root
        self.root.title("Visualização de Coordenadas no Mapa")
        self.coordenadas = coordenadas_iniciais if coordenadas_iniciais else []
        self.mapa_arquivo = None
        self.nome_arquivo_json = "coordenadas.json"
        self.nome_arquivo_xml = "coordenadas.xml"
        self.nome_arquivo_csv = "coordenadas.csv"

        self.frame_entrada = ttk.LabelFrame(root, text="Adicionar Coordenada")
        self.frame_entrada.pack(padx=10, pady=10, fill="x")

        self.lbl_nome = ttk.Label(self.frame_entrada, text="Nome:")
        self.lbl_nome.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.ent_nome = ttk.Entry(self.frame_entrada)
        self.ent_nome.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.lbl_latitude = ttk.Label(self.frame_entrada, text="Latitude:")
        self.lbl_latitude.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ent_latitude = ttk.Entry(self.frame_entrada)
        self.ent_latitude.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.lbl_longitude = ttk.Label(self.frame_entrada, text="Longitude:")
        self.lbl_longitude.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.ent_longitude = ttk.Entry(self.frame_entrada)
        self.ent_longitude.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.btn_adicionar = ttk.Button(self.frame_entrada, text="Adicionar", command=self.adicionar_coordenada)
        self.btn_adicionar.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        self.frame_lista = ttk.LabelFrame(root, text="Coordenadas Atuais")
        self.frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.frame_lista)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lista_coordenadas = tk.Listbox(self.frame_lista, yscrollcommand=self.scrollbar.set, height=5)
        self.lista_coordenadas.pack(padx=5, pady=5, fill="both", expand=True)
        self.scrollbar.config(command=self.lista_coordenadas.yview)

        self.btn_abrir = ttk.Button(root, text="Abrir Mapa no Navegador", command=self.abrir_mapa)
        self.btn_abrir.pack(pady=10)

        self.lbl_instrucao = ttk.Label(root, text="O mapa será aberto no seu navegador padrão.")
        self.lbl_instrucao.pack(pady=5)

        # Exportar as coordenadas iniciais ao iniciar o aplicativo
        if self.coordenadas:
            self.atualizar_lista_coordenadas()
            self.exportar_json(self.nome_arquivo_json)
            self.exportar_xml(self.nome_arquivo_xml)
            self.exportar_csv(self.nome_arquivo_csv)

        self.atualizar_mapa()

    def criar_mapa(self):
        # Cria um mapa Folium com as coordenadas atuais e o salva como HTML.
        if not self.coordenadas:
            messagebox.showinfo("Aviso", "Nenhuma coordenada para exibir no mapa.")
            return None

        df = pd.DataFrame(self.coordenadas)
        geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
        gdf = geopandas.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

        if not gdf.empty:
            mean_lat = gdf['latitude'].mean()
            mean_lon = gdf['longitude'].mean()
            m = folium.Map(location=[mean_lat, mean_lon], zoom_start=10)
            for index, row in gdf.iterrows():
                nome = row.get('nome', 'Sem Nome')
                latitude = row['latitude']
                longitude = row['longitude']
                folium.Marker(
                    location=[latitude, longitude],
                    popup=f"<b>{nome}</b><br>Latitude: {latitude}<br>Longitude: {longitude}"
                ).add_to(m)
        else:
            m = folium.Map(location=[0, 0], zoom_start=2) # Mapa padrão se não houver coordenadas

        map_filename = "mapa_tkinter.html"
        m.save(map_filename)
        return map_filename

    def adicionar_coordenada(self):
        # Adiciona a coordenada inserida à lista e atualiza o mapa e os arquivos. 
        nome = self.ent_nome.get().strip()
        try:
            latitude = float(self.ent_latitude.get())
            longitude = float(self.ent_longitude.get())
            nova_coordenada = {'nome': nome, 'latitude': latitude, 'longitude': longitude}
            self.coordenadas.append(nova_coordenada)
            self.ent_nome.delete(0, tk.END)
            self.ent_latitude.delete(0, tk.END)
            self.ent_longitude.delete(0, tk.END)
            self.atualizar_lista_coordenadas()
            self.atualizar_mapa()
            self.exportar_json(self.nome_arquivo_json)
            self.exportar_xml(self.nome_arquivo_xml)
            self.exportar_csv(self.nome_arquivo_csv)
            messagebox.showinfo("Sucesso", "Coordenada adicionada e arquivos atualizados. Por favor, recarregue a página do mapa no seu navegador (F5).")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos para latitude e longitude.")

    def atualizar_lista_coordenadas(self):
        # Atualiza a listbox com as coordenadas atuais.
        self.lista_coordenadas.delete(0, tk.END)
        for coord in self.coordenadas:
            self.lista_coordenadas.insert(tk.END, f"{coord.get('nome', 'Sem Nome')} ({coord['latitude']:.4f}, {coord['longitude']:.4f})")

    def atualizar_mapa(self):
        """Gera um novo mapa com as coordenadas atuais."""
        self.mapa_arquivo = self.criar_mapa()
        if self.mapa_arquivo:
            pass

    def abrir_mapa(self):
        """Abre o arquivo HTML do mapa no navegador padrão."""
        if self.mapa_arquivo:
            webbrowser.open("file://" + os.path.abspath(self.mapa_arquivo))
        else:
            messagebox.showinfo("Aviso", "Nenhum mapa foi gerado ainda.")

    def exportar_json(self, file_path=None):
        # Exporta as coordenadas para um arquivo JSON.
        if not self.coordenadas:
            return

        if file_path is None:
            file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                    filetypes=[("JSON files", "*.json"), ("Todos os arquivos", "*.*")])
            if not file_path:
                return

        try:
            with open(file_path, 'w') as f:
                json.dump({'coordenadas': self.coordenadas}, f, indent=4)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar para JSON: {e}")

    def exportar_xml(self, file_path=None):
        # Exporta as coordenadas para um arquivo XML.
        if not self.coordenadas:
            return

        if file_path is None:
            file_path = filedialog.asksaveasfilename(defaultextension=".xml",
                                                    filetypes=[("XML files", "*.xml"), ("Todos os arquivos", "*.*")])
            if not file_path:
                return

        try:
            root_xml = ET.Element("coordenadas")
            for coord in self.coordenadas:
                ponto = ET.SubElement(root_xml, "ponto")
                nome = ET.SubElement(ponto, "nome")
                nome.text = coord.get('nome', '')
                latitude = ET.SubElement(ponto, "latitude")
                latitude.text = str(coord['latitude'])
                longitude = ET.SubElement(ponto, "longitude")
                longitude.text = str(coord['longitude'])

            xml_str = minidom.parseString(ET.tostring(root_xml)).toprettyxml(indent="  ")
            with open(file_path, 'w') as f:
                f.write(xml_str)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar para XML: {e}")

    def exportar_csv(self, file_path=None):
        # Exporta as coordenadas para um arquivo CSV.
        if not self.coordenadas:
            return

        if file_path is None:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV files", "*.csv"), ("Todos os arquivos", "*.*")])
            if not file_path:
                return

        try:
            df = pd.DataFrame(self.coordenadas)
            df.to_csv(file_path, index=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar para CSV: {e}")

if __name__ == "__main__":
    coordenadas_iniciais = [
        {'nome': 'Sao Paulo', 'latitude': -23.5505, 'longitude': -46.6333},
        {'nome': 'Rio de Janeiro', 'latitude': -22.9068, 'longitude': -43.1729},
    ]
    root = tk.Tk()
    app = MapaTkinterApp(root, coordenadas_iniciais)
    root.mainloop()