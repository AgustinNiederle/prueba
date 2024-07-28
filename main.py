from fastapi import FastAPI, HTTPException
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('stopwords')

app = FastAPI()


df = pd.read_parquet(r'df_reducido_prueba.parquet')
df = pd.DataFrame(df)
df['overviews'] = df['overview'].fillna('')

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    return ' '.join([word for word in words if word.isalpha() and word not in stop_words])

df['clean_overviews'] = df['overviews'].apply(preprocess_text)

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['clean_overviews'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
cosine_sim_df = pd.DataFrame(cosine_sim, index=df['title'], columns=df['title'])

@app.get("/recomendacion/{title}")
def get_recommendation(title: str, top_n: int = 5):
    if title not in cosine_sim_df.index:
        raise HTTPException(status_code=404, detail=f'El titulo "{title}" no fue encontrado en la colección. Por favor, ingrese otro titulo en inglés.')
    
    sim_scores = cosine_sim_df[title]
      
    sim_scores = sim_scores.drop(title).sort_values(ascending=False)
    
    top_similar_titles = sim_scores.head(top_n).index.tolist()
    return {f"Si te gustó {title}, también podrían interesarte: {top_similar_titles}"}

#sumo estas listas que voy a necesitar
dias = {
    "lunes": 0,
    "martes": 1,
    "miércoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sábado": 5,
    "domingo": 6
}

meses = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12
}

@app.get("/cantidad_de_estrenos_mes/{mes}")
def get_fecha(mes: str):
    
    mes = mes.lower()
    # Verifico si el nombre del mes es válido
    if mes not in meses:
        raise HTTPException(status_code=400, detail="Mes inválido. Los meses válidos son: " + ", ".join(meses.keys()))

    #convierto
    mes_num = meses[mes]

    # Convierto la columna de fecha a datetime
    df['release_date'] = pd.to_datetime(df['release_date'])

    filtered_df = df[df['release_date'].dt.month == mes_num]
    count = filtered_df.shape[0]

    return {f"En el mes de {mes} se estrenaron un total de {count} películas"}


@app.get("/cantidad_de_estrenos_dia/{dia}")
def get_fecha(dia: str):
    # Convertir el nombre del día a minúsculas
    dia = dia.lower()

    # Verificar si el nombre del día es válido
    if dia not in dias:
        raise HTTPException(status_code=400, detail="Día inválido. Los días válidos son: " + ", ".join(dias.keys()))

    # Convertir el nombre del día a su correspondiente número
    dia_num = dias[dia]

    # Convertir la columna de fecha a datetime
    df['release_date'] = pd.to_datetime(df['release_date'])

    # Filtrar el DataFrame por el día de la semana indicado
    filtered_df = df[df['release_date'].dt.dayofweek == dia_num]
    count = filtered_df.shape[0]

    return {f"En el día {dia.capitalize()} se estrenaron un total de {count} películas"}


@app.get("/score_titulo/{titulo}")
def score_titulo(titulo: str):
    df = pd.read_parquet(r'df_reducido_prueba.parquet')
    
    # Filtrar el DataFrame por el título
    filtered_df = df[df['title'] == titulo]
    
    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="Título no encontrado")
    
    # Obtener el año de estreno y la popularidad
    release_year = filtered_df["release_date"].dt.year.values[0]
    popularity = filtered_df["popularity"].values[0]
    vote = filtered_df["vote_average"].values[0]
    return {f"El título {titulo} fue estrenado el año {int(release_year)} con un promedio de votos de {vote} y una popularidad de {float(popularity):.2f}"}


@app.get("/titulo_del_film/{titulo}")
def titulo_del_film(titulo: str):
    df = pd.read_parquet(r'df_reducido_prueba.parquet')
      
    filtered_df = df[df['title'] == titulo]
    
    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="Título no encontrado")
    
    release_year = filtered_df["release_date"].dt.year.values[0]
    vote_average = filtered_df["vote_average"].values[0]
    count_vote = filtered_df["vote_count"].values[0]

    # Pra verificar si el conteo de votos es mayor a 2000
    if count_vote > 2000:
        return {f"El film {titulo} fue estrenado el año {int(release_year)}, cuenta con un total de valoraciones de {int(count_vote)} y con un promedio de votos de {float(vote_average):.2f}"}
    else:
        return {
            "mensaje": f"El film {titulo} no cumple con la condición de tener más de 2000 votos, tiene {int(count_vote)} votos."
        }

#probar con Alice in Wonderland para mostrar què pasa si tiene menos de 2000 votos

@app.get("/actor_actriz/{nombre_actor_actriz}")
def get_actor(nombre_actor_actriz: str):
    df = pd.read_parquet(r'df_reducido_prueba.parquet')
    
    filtered_df = df[df['Cast'].str.contains(nombre_actor_actriz, case=False, na=False)]
    
    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="Actor/Actriz no encontrado")
    
    movies = filtered_df["title"].count()
    
    succes = filtered_df["vote_average"].mean()
      
    gain_avg = filtered_df["return"].mean()
    
    return {
        "mensaje": f"{nombre_actor_actriz} participó en {int(movies)} películas, tiene un éxito promedio de {float(succes):.2f} y una ganancia promedio de {float(gain_avg):.2f} millones"
    }
    
@app.get("/nombre_director_a/{nombre_director_a}")
def get_director(nombre_director_a: str):
    df = pd.read_parquet(r'df_reducido_prueba.parquet')
    
    filtered_df = df[df['Directed by'].str.contains(nombre_director_a, case=False, na=False)]
    
    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="Director/Directora no encontrado/a")
    
    movies = filtered_df["title"].count()
    
    succes = filtered_df["vote_average"].mean()
      
    gain_avg = filtered_df["return"].mean()
    
    return {
        "mensaje": f"{nombre_director_a} dirigió {int(movies)} película/s, tiene un éxito promedio de {float(succes):.2f} y una ganancia promedio de {float(gain_avg):.2f} millones por película"
    }
