from fastapi import FastAPI, HTTPException
import pandas as pd

app = FastAPI()

df = pd.read_parquet(r'df_reducido_prueba.parquet')

@app.get("/cantidad_de_estrenos_mes/{mes}")
def get_fecha(mes: int):
    # Convertir la columna de fecha a datetime
    df['release_date'] = pd.to_datetime(df['release_date'])

    # Filtrar el DataFrame por el mes indicado
    filtered_df = df[df['release_date'].dt.month == mes]
    count = filtered_df.shape[0]

    return {f"En el mes {mes} se estrenaron un Total de {count} películas"}

@app.get("/cantidad_de_estrenos_dia/{dia}")
def get_fecha(dia: int):
    # Convertir la columna de fecha a datetime
    df['release_date'] = pd.to_datetime(df['release_date'])

    # Filtrar el DataFrame por el mes indicado
    filtered_df = df[df['release_date'].dt.day == dia]
    count = filtered_df.shape[0]

    return {f"En el dia {dia} se estrenaron un Total de {count} películas"}

#ahora necesito que los meses y los dias se ingresen en texto

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

