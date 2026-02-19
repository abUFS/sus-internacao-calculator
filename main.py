from fastapi import FastAPI, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from domain.models import CalcRequest, Procediment

from domain.rules import days_in_each_month, calc_perm_maior, get_media_perm

from collections import Counter

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

procediments: list[dict] = [
    {'code': '0301010170',
     'name': 'nome a 1',
     'avrg_stay': 4
    },
    {'code': '0410010111',
     'name': 'nome b 2',
     'avrg_stay': 3
    },
    {'code': '0301010176',
     'name': 'nome c 3',
     'avrg_stay': 2
    }
]


#TODO limpar rotas

@app.get("/", include_in_schema=False, name="home")
def home(request: Request) -> str:
    return templates.TemplateResponse(request, 
                                      "home.html", 
                                      {"procediments": procediments, "title":"Home"})

@app.get("/info", include_in_schema=False, name="info")
def calc(request: Request) -> str:
    return templates.TemplateResponse(request, 
                                      "info.html", 
                                      {"procediments": procediments, "title":"Calc"})


@app.get("/api/procedimentos/search")
def search(q: str):
    sugested_procs = []
    for i, proc in enumerate(procediments):
        if i < 10:
            if q in proc.get('code'):
                sugested_procs.append(proc)
    
    return { "proclist": sugested_procs}

@app.get("/api/proc_id/{nome}")
def get_codigo(nome: str) -> list[dict]:
    temp_proc = []
    for i, proc in enumerate(procediments):
        if i < 19:
            if nome in proc.get('nome'):
                temp_proc.append(proc)
    
    return temp_proc

@app.get("/api/media_perm/{codigo}")
def get_mean_stay(codigo: str) -> dict[str, int]:
    result = get_media_perm(codigo, procediments)
    if result:
        return {'media_perm': result}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="codigo não encontrado.")

@app.post("/api/calc/")
def calculate(data: CalcRequest):

    #TODO separar em funções adequadas
    too_big_interval = False
    hospitalization = data.hospitalization
    try:
        too_big_interval = (hospitalization.end.year - hospitalization.start.year) > 500
    except:
        too_big_interval = True

    if too_big_interval:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Intervalo muito longo.")
    
    if hospitalization.start > hospitalization.end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Data inicial anterior a data final.")

    #Perm a maior
    print(data.procediment.code)
    avrg_stay = get_media_perm(data.procediment.code, procediments)
    if not avrg_stay:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Procedimento inválido.")
    
    long_stay = calc_perm_maior(hospitalization.start, hospitalization.end, avrg_stay)

    #Diarias total
    competences = days_in_each_month(hospitalization.start, hospitalization.end)
    
    #Diarias UTI
    itu_competences = [days_in_each_month(p.start, p.end) for p in data.itu_periods]
    total_itu_competences = Counter()
    for itu_comp in itu_competences:
        total_itu_competences.update(itu_comp)
    total_itu_competences = dict(total_itu_competences)

    #Diarias efetivas
    effective_competences = dict()
    for key, value in competences.items():
        itu_comp_value = total_itu_competences.get(key, 0)
        effective_competences[key] = value - itu_comp_value
        #Reduzir perm a maior pela quantidade de UTI
        long_stay -= itu_comp_value
    long_stay = long_stay if long_stay > 0 else 0 # Não pode ser negativo
    
    return {'perm': long_stay, 'competencias_total': competences, 'competencias_UTI': total_itu_competences, 'competencias_efetivo':effective_competences}

#TODO adicionar tratamento de exceções padronizado