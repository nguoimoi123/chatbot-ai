# Data Ingestion Script for Football Data into AstraDB
import os
from dotenv import load_dotenv
load_dotenv()  
import time
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from astrapy import DataAPIClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FootballDataIngestion:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.astra_client = DataAPIClient()
        self.db = self.astra_client.get_database(
            os.environ.get('ASTRA_DB_ENDPOINT'),
            token=os.environ.get('ASTRA_DB_APPLICATION_TOKEN')
        )
        self.collection_name = os.environ.get('ASTRA_DB_COLLECTION')
        self.chunk_size = 1000
        self.chunk_overlap = 200

    def create_collection(self):
        """Create collection if it doesn't exist."""
        try:
            if self.collection_name in self.db.list_collections():
                logging.info(f"Collection '{self.collection_name}' already exists.")
                return
            
            self.db.create_collection(
                self.collection_name,
                options={"vector": {"dimension": 1536, "metric": "cosine"}}
            )
            logging.info(f"Collection '{self.collection_name}' created successfully.")
        except Exception as e:
            logging.error(f"Error creating collection: {e}")

    def scrape_content(self, url):
        """Scrape text content from a Wikipedia URL."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get the main content div of Wikipedia
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if not content_div:
                return ""
            
            # Remove unwanted tags
            for tag in content_div.find_all(['table', 'script', 'style', 'sup']):
                tag.decompose()
            
            text = content_div.get_text(separator='\n', strip=True)
            return text
        except Exception as e:
            logging.error(f"Failed to scrape {url}: {e}")
            return ""

    def split_text(self, text):
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap if end < len(text) else end
        return [c for c in chunks if len(c.strip()) > 50]

    async def ingest_data(self, urls):
        """Main function to scrape, embed, and insert data."""
        self.create_collection()
        collection = self.db.get_collection(self.collection_name)
        
        total_inserted = 0
        for i, url in enumerate(urls):
            logging.info(f"Processing URL {i+1}/{len(urls)}: {url}")
            content = self.scrape_content(url)
            if not content:
                continue

            chunks = self.split_text(content)
            logging.info(f"  -> Split into {len(chunks)} chunks.")

            for j, chunk in enumerate(chunks):
                try:
                    embedding_response = self.openai_client.embeddings.create(
                        model="text-embedding-3-small",
                        input=chunk,
                        encoding_format="float"
                    )
                    vector = embedding_response.data[0].embedding

                    collection.insert_one({
                        "$vector": vector,
                        "text": chunk,
                        "source": url
                    })
                    total_inserted += 1
                    # Add a small delay to avoid rate limits
                    time.sleep(0.1) 
                except Exception as e:
                    logging.error(f"    -> Failed to insert chunk {j}: {e}")
        
        logging.info(f"Data ingestion completed. Total chunks inserted: {total_inserted}")

# --- DANH SÁCH 100 LINK WIKIPEDIA VỀ BÓNG ĐÁ ---
FOOTBALL_URLS = [
    # Giải đấu Quốc tế
   "https://vi.wikipedia.org/wiki/Gi%E1%BA%A3i_v%C3%B4_%C4%91%E1%BB%8Bch_b%C3%B3ng_%C4%91%C3%A1_th%E1%BA%BF_gi%E1%BB%9Bi",
    "https://vi.wikipedia.org/wiki/Gi%E1%BA%A3i_v%C3%B4_%C4%91%E1%BB%8Bch_b%C3%B3ng_%C4%91%C3%A1_ch%C3%A2u_%C3%82u",
    "https://vi.wikipedia.org/wiki/Copa_Am%C3%A9rica",
    "https://vi.wikipedia.org/wiki/Cúp_b%C3%B3ng_%C4%91%C3%A1_ch%C3%A2u_%C3%81",
    "https://vi.wikipedia.org/wiki/Gi%E1%BA%A3i_v%C3%B4_%C4%91%E1%BB%8Bch_b%C3%B3ng_%C4%91%C3%A1_ch%C3%A2u_%C3%81",
    "https://vi.wikipedia.org/wiki/Gi%E1%BA%A3i_v%C3%B4_%C4%91%E1%BB%8Bch_b%C3%B3ng_%C4%91%C3%A1_U-20_th%E1%BA%BF_gi%E1%BB%9Bi",
    "https://vi.wikipedia.org/wiki/Gi%E1%BA%A3i_v%C3%B4_%C4%91%E1%BB%8Bch_b%C3%B3ng_%C4%91%C3%A1_n%E1%BB%AF_th%E1%BA%BF_gi%E1%BB%9bi",
    "https://vi.wikipedia.org/wiki/Confederations_Cup",
    "https://vi.wikipedia.org/wiki/Si%C3%AAu_c%C3%BAp_ch%C3%A2u_%C3%82u",
    "https://vi.wikipedia.org/wiki/Si%C3%AAu_c%C3%BAp_ch%C3%A2u_M%E1%BB%B9",
    "https://vi.wikipedia.org/wiki/C%C3%BAp_C1_ch%C3%A2u_%C3%82u",
    "https://vi.wikipedia.org/wiki/UEFA_Youth_League",
    "https://vi.wikipedia.org/wiki/C%C3%BAp_b%C3%B3ng_%C4%91%C3%A1_U-23_ch%C3%A2u_%C3%81",
    "https://vi.wikipedia.org/wiki/Asian_Cup",
    "https://vi.wikipedia.org/wiki/Gi%E1%BA%A3i_v%C3%B4_%C4%91%E1%BB%8Bch_b%C3%B3ng_%C4%91%C3%A1_%C4%90%C3%B4ng_Nam_%C3%81",
    "https://vi.wikipedia.org/wiki/UEFA_Nations_League",
    "https://vi.wikipedia.org/wiki/C%C3%BAp_CAF",
    "https://vi.wikipedia.org/wiki/C%C3%BAp_v%C3%B4_%C4%91%E1%BB%8Bch_qu%E1%BB%91c-gia_%C3%9ac",
    "https://vi.wikipedia.org/wiki/Gi%E1%BA%A3i_v%C3%B4_%C4%91%E1%BB%8Bch_b%C3%B3ng_%C4%91%C3%A1_ch%C3%A2u_M%E1%BB%B9",
    "https://vi.wikipedia.org/wiki/V.League_2",
    "https://vi.wikipedia.org/wiki/C%C3%BAp_National",
    "https://vi.wikipedia.org/wiki/CONCACAF_Gold_Cup",
    "https://vi.wikipedia.org/wiki/Gi%E1%BA%A3i_v%C3%B4_%C4%91%E1%BB%8Bch_b%C3%B3ng_%C4%91%C3%A1_U-17_th%E1%BA%BF_gi%E1%BB%9bi",
    "https://vi.wikipedia.org/wiki/Gi%E1%BA%A3i_v%C3%B4_%C4%91%E1%BB%8Bch_b%C3%B3ng_%C4%91%C3%A1_club_th%E1%BA%BF_gi%E1%BB%9i",

    # Giải đấu Câu lạc bộ (Châu Âu)
    "https://vi.wikipedia.org/wiki/UEFA_Champions_League",
    "https://vi.wikipedia.org/wiki/UEFA_Europa_League",
    "https://vi.wikipedia.org/wiki/UEFA_Europa_Conference_League",
    "https://vi.wikipedia.org/wiki/Si%C3%AAu_c%C3%BAp_b%C3%B3ng_%C4%91%C3%A1_ch%C3%A2u_%C3%82u",
    "https://vi.wikipedia.org/wiki/Premier_League",
    "https://vi.wikipedia.org/wiki/La_Liga",
    "https://vi.wikipedia.org/wiki/Serie_A",
    "https://vi.wikipedia.org/wiki/Bundesliga",
    "https://vi.wikipedia.org/wiki/Ligue_1",
    "https://vi.wikipedia.org/wiki/Eredivisie",
    "https://vi.wikipedia.org/wiki/Primeira_Liga",
    "https://vi.wikipedia.org/wiki/V.League_1",
    "https://vi.wikipedia.org/wiki/S%C3%A9rie_A_(Brazil)",
    "https://vi.wikipedia.org/wiki/Primera_Divisi%C3%B3n_(Argentina)",
    "https://vi.wikipedia.org/wiki/MLS",
    "https://vi.wikipedia.org/wiki/J1_League",
    "https://vi.wikipedia.org/wiki/K_League_1",
    "https://vi.wikipedia.org/wiki/Russian_Premier_League",
    "https://vi.wikipedia.org/wiki/S%C3%BCper_Lig",
    "https://vi.wikipedia.org/wiki/S%C3%A9rie_B_(Brazil)",
    "https://vi.wikipedia.org/wiki/Chinese_Super_League",
    "https://vi.wikipedia.org/wiki/Scottish_Professional_Football_League",
    "https://vi.wikipedia.org/wiki/Ukrainian_Premier_League",
    "https://vi.wikipedia.org/wiki/Belgian_Pro_League",
    "https://vi.wikipedia.org/wiki/English_Football_League",
    "https://vi.wikipedia.org/wiki/Serie_B_(Italy)",
    "https://vi.wikipedia.org/wiki/2._Bundesliga",
    "https://vi.wikipedia.org/wiki/La_Liga_2",
    "https://vi.wikipedia.org/wiki/Ligue_2",
    "https://vi.wikipedia.org/wiki/EFL_Championship",

    # Giải đấu Quốc gia hàng đầu
    "https://vi.wikipedia.org/wiki/Premier_League",
    "https://vi.wikipedia.org/wiki/La_Liga",
    "https://vi.wikipedia.org/wiki/Serie_A",
    "https://vi.wikipedia.org/wiki/Bundesliga",
    "https://vi.wikipedia.org/wiki/Ligue_1",
    "https://vi.wikipedia.org/wiki/Eredivisie",
    "https://vi.wikipedia.org/wiki/Primeira_Liga",
    "https://vi.wikipedia.org/wiki/V.League_1",

    # Các CLB Lịch sử
    "https://vi.wikipedia.org/wiki/Real_Madrid_C.F.",
    "https://vi.wikipedia.org/wiki/FC_Barcelona",
    "https://vi.wikipedia.org/wiki/Manchester_United_F.C.",
    "https://vi.wikipedia.org/wiki/Liverpool_F.C.",
    "https://vi.wikipedia.org/wiki/Arsenal_F.C.",
    "https://vi.wikipedia.org/wiki/Chelsea_F.C.",
    "https://vi.wikipedia.org/wiki/Manchester_City_F.C.",
    "https://vi.wikipedia.org/wiki/Bayern_Munich",
    "https://vi.wikipedia.org/wiki/Borussia_Dortmund",
    "https://vi.wikipedia.org/wiki/Juventus_F.C.",
    "https://vi.wikipedia.org/wiki/A.C._Milan",
    "https://vi.wikipedia.org/wiki/Inter_Milan",
    "https://vi.wikipedia.org/wiki/Paris_Saint-Germain_F.C.",
    "https://vi.wikipedia.org/wiki/Olympique_de_Marseille",
    "https://vi.wikipedia.org/wiki/Ajax_Amsterdam",
    "https://vi.wikipedia.org/wiki/Porto",
    "https://vi.wikipedia.org/wiki/SL_Benfica",
    "https://vi.wikipedia.org/wiki/Celtic_F.C.",
    "https://vi.wikipedia.org/wiki/Rangers_F.C.",
    "https://vi.wikipedia.org/wiki/Sevilla_FC",

    # Huyền thoại Bóng đá
    "https://vi.wikipedia.org/wiki/Pel%C3%A9",
    "https://vi.wikipedia.org/wiki/Diego_Maradona",
    "https://vi.wikipedia.org/wiki/Johan_Cruyff",
    "https://vi.wikipedia.org/wiki/Franz_Beckenbauer",
    "https://vi.wikipedia.org/wiki/Michel_Platini",
    "https://vi.wikipedia.org/wiki/Marco_van_Basten",
    "https://vi.wikipedia.org/wiki/Roberto_Baggio",
    "https://vi.wikipedia.org/wiki/Lothar_Matth%C3%A4us",
    "https://vi.wikipedia.org/wiki/Zin%C3%A9dine_Zidane",
    "https://vi.wikipedia.org/wiki/Ronaldo",
    "https://vi.wikipedia.org/wiki/Ronaldinho",
    "https://vi.wikipedia.org/wiki/Frank_Lampard",
    "https://vi.wikipedia.org/wiki/Steven_Gerrard",
    "https://vi.wikipedia.org/wiki/Xavi",
    "https://vi.wikipedia.org/wiki/Andres_Iniesta",
    "https://vi.wikipedia.org/wiki/Iker_Casillas",
    "https://vi.wikipedia.org/wiki/Carles_Puyol",
    "https://vi.wikipedia.org/wiki/Paolo_Maldini",
    "https://vi.wikipedia.org/wiki/Alessandro_Nesta",
    "https://vi.wikipedia.org/wiki/Fabio_Cannavaro",
    "https://vi.wikipedia.org/wiki/Gianluigi_Buffon",
    "https://vi.wikipedia.org/wiki/Oliver_Kahn",
    "https://vi.wikipedia.org/wiki/George_Best",
    "https://vi.wikipedia.org/wiki/Alfredo_Di_St%C3%A9fano",
    "https://vi.wikipedia.org/wiki/Ferenc_Pusk%C3%A1s",
    "https://vi.wikipedia.org/wiki/Eus%C3%A9bio",
    "https://vi.wikipedia.org/wiki/Lev_Yashin",
    "https://vi.wikipedia.org/wiki/Gordon_Banks",

    # Các Ngôi sao Hiện tại
    "https://vi.wikipedia.org/wiki/Lionel_Messi",
    "https://vi.wikipedia.org/wiki/Cristiano_Ronaldo",
    "https://vi.wikipedia.org/wiki/Neymar",
    "https://vi.wikipedia.org/wiki/Kylian_Mbapp%C3%A9",
    "https://vi.wikipedia.org/wiki/Erling_Haaland",
    "https://vi.wikipedia.org/wiki/Jude_Bellingham",
    "https://vi.wikipedia.org/wiki/Vin%C3%ADcius_J%C3%BAnior",
    "https://vi.wikipedia.org/wiki/Kevin_De_Bruyne",
    "https://vi.wikipedia.org/wiki/Robert_Lewandowski",
    "https://vi.wikipedia.org/wiki/Mohamed_Salah",
    "https://vi.wikipedia.org/wiki/Harry_Kane",
    "https://vi.wikipedia.org/wiki/Luka_Modri%C4%87",
    "https://vi.wikipedia.org/wiki/Karim_Benzema",
    "https://vi.wikipedia.org/wiki/Antoine_Griezmann",
    "https://vi.wikipedia.org/wiki/Virgil_van_Dijk",
    "https://vi.wikipedia.org/wiki/Sadio_Man%C3%A9",
    "https://vi.wikipedia.org/wiki/Eden_Hazard",
    "https://vi.wikipedia.org/wiki/Sergio_Ramos",
    "https://vi.wikipedia.org/wiki/Gerard_Piqu%C3%A9",
    "https://vi.wikipedia.org/wiki/Toni_Kroos",
    "https://vi.wikipedia.org/wiki/Ederson",
    "https://vi.wikipedia.org/wiki/Alisson_Becker",

    # Bóng đá Việt Nam
    "https://vi.wikipedia.org/wiki/%C4%90%E1%BB%99i_tuy%E1%BB%83n_b%C3%B3ng_%C4%91%C3%A1_qu%E1%BB%91c_gia_Vi%E1%BB%87t_Nam",
    "https://vi.wikipedia.org/wiki/Park_Hang-seo",
    "https://vi.wikipedia.org/wiki/Philippe_Troussier",
    "https://vi.wikipedia.org/wiki/Nguy%E1%BB%85n_Qu%E1%BA%A3i_H%E1%BA%A3i",
    "https://vi.wikipedia.org/wiki/L%C3%AA_C%C3%B4ng_Vinh",
    "https://vi.wikipedia.org/wiki/Ph%E1%BA%A1m_V%C4%83n_Quy%E1%BA%BFt",
    "https://vi.wikipedia.org/wiki/Nguy%E1%BB%85n_C%C3%B4ng_Ph%C6%B0%C6%A1ng",
    "https://vi.wikipedia.org/wiki/Qu%E1%BA%A3ng_H%E1%BA%A3i",
    "https://vi.wikipedia.org/wiki/H%C3%A0i_Long",
    "https://vi.wikipedia.org/wiki/Ho%C3%A0ng_L%E1%BA%A1c",
    "https://vi.wikipedia.org/wiki/Vi%E1%BB%87t_T%C3%A2m",
    "https://vi.wikipedia.org/wiki/H%C3%A0_Noi_FC",
    "https://vi.wikipedia.org/wiki/H%E1%BB%93ng_L%C3%Anh_Anh_H%C3%A0_N%E1%BB%99i",
    "https://vi.wikipedia.org/wiki/Th%C3%A1i_Nguyen",
    "https://vi.wikipedia.org/wiki/Becamex_Binh_Duong",
    "https://vi.wikipedia.org/wiki/SHB_%C4%90%C3%A0_N%E1%BA%B5ng",

    # Các khái niệm & Lịch sử
    "https://vi.wikipedia.org/wiki/L%E1%BB%8Bch_s%E1%BB%AD_b%C3%B3ng_%C4%91%C3%A1",
    "https://vi.wikipedia.org/wiki/Lu%E1%BA%ADt_b%C3%B3ng_%C4%91%C3%A1",
    "https://vi.wikipedia.org/wiki/Vi%E1%BB%87t_v%E1%BB%8B_(b%C3%B3ng_%C4%91%C3%A1)",
    "https://vi.wikipedia.org/wiki/T%C3%AC_th%E1%BA%A5t_(b%C3%B3ng_%C4%91%C3%A1)",
    "https://vi.wikipedia.org/wiki/Tiki-taka",
    "https://vi.wikipedia.org/wiki/Catenaccio",
    "https://vi.wikipedia.org/wiki/False_9",
    "https://vi.wikipedia.org/wiki/FIFA",
    "https://vi.wikipedia.org/wiki/UEFA",
    "https://vi.wikipedia.org/wiki/B%C3%B3ng_%C4%91%C3%A1_n%E1%BB%AF",
    "https://vi.wikipedia.org/wiki/Qu%E1%BA%A3_b%C3%B3ng_v%C3%A0ng",
    "https://vi.wikipedia.org/wiki/Chi%E1%BA%BFc_gi%C3%A0y_v%C3%A0ng",
    "https://vi.wikipedia.org/wiki/Chi%E1%BA%BFc_gi%C3%A0y_%C4%91%E1%BB%8F",
]

if __name__ == "__main__":
    import asyncio
    
    # Make sure to install beautifulsoup4 and requests
    # pip install beautifulsoup4 requests
    
    ingestion = FootballDataIngestion()
    asyncio.run(ingestion.ingest_data(FOOTBALL_URLS))