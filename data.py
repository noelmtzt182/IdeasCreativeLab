"""Contenido estático: métodos, técnicas, pasos guía, sombreros, principios TRIZ."""

# Paleta de marca: usada por styles.py y ui.py para pintar la app.
THEME = {
    "primary": "#6D28D9",       # violeta vívido, color de marca principal
    "primary_dark": "#4C1D95",
    "bg": "#FFFDF9",             # blanco cálido, no genérico
    "surface": "#FFFFFF",
    "surface_tint": "#F5F1FF",   # lavanda muy claro, para tarjetas/sidebar
    "ink": "#1B1B2F",            # casi negro azulado, alto contraste
    "ink_soft": "#4B4B63",
    "line": "#E4DFF5",
    "success": "#0CA678",
    "warning": "#F59F00",
    "danger": "#E03131",
    "font_display": "Fredoka",
    "font_body": "Nunito Sans",
}

METHODS = [
    {
        "id": "design-thinking", "name": "Design Thinking", "code": "DT", "color": "#D6336C", "text_on": "white",
        "category": "metodo", "orientation": "Empatía y el usuario final",
        "tagline": "De entender a las personas a probar una solución, paso a paso.",
        "best_for": "Diseñar productos, servicios y experiencias de usuario.", "time": "45–60 min",
    },
    {
        "id": "double-diamond", "name": "Double Diamond", "code": "DD", "color": "#7048E8", "text_on": "white",
        "category": "metodo", "orientation": "Claridad en la definición del problema y la solución",
        "tagline": "Dos rombos: abre para explorar, cierra para decidir. Dos veces.",
        "best_for": "Procesos de diseño estratégico y gestión de proyectos.", "time": "40–60 min",
    },
    {
        "id": "cps", "name": "CPS · Creative Problem Solving", "code": "CP", "color": "#E8590C", "text_on": "white",
        "category": "metodo", "orientation": "Equilibrio de pensamiento analítico e imaginativo",
        "tagline": "Del reto a la implementación, alternando entre imaginar y decidir.",
        "best_for": "Resolver problemas abstractos o bloqueos organizacionales.", "time": "40–55 min",
    },
    {
        "id": "triz", "name": "TRIZ", "code": "TZ", "color": "#0CA678", "text_on": "white",
        "category": "metodo", "orientation": "Lógica, leyes de patentes y sistemas técnicos",
        "tagline": "Resuelve contradicciones técnicas con 40 principios de inventiva.",
        "best_for": "Innovación tecnológica, ingeniería y manufactura de hardware.", "time": "30–40 min",
    },
    {
        "id": "foresight", "name": "Foresight · Previsión Estratégica", "code": "FS", "color": "#1098AD", "text_on": "white",
        "category": "metodo", "orientation": "Anticipar el futuro antes de que te alcance",
        "tagline": "No adivina el futuro: explora varios futuros posibles para decidir mejor hoy.",
        "best_for": "Anticipar riesgos, tendencias o cambios de contexto antes de comprometerte con un plan.",
        "time": "35–50 min",
    },
    {
        "id": "scamper", "name": "SCAMPER", "code": "SC", "color": "#3B5BDB", "text_on": "white",
        "category": "tecnica", "orientation": "Transformación sistemática de algo existente",
        "tagline": "Transforma algo que ya existe con 7 lentes de cambio.",
        "best_for": "Mejorar un producto, servicio o proceso que ya tienes.", "time": "20–30 min",
    },
    {
        "id": "six-hats", "name": "Seis Sombreros para Pensar", "code": "6S", "color": "#495057", "text_on": "white",
        "category": "tecnica", "orientation": "Separar los tipos de pensamiento al evaluar",
        "tagline": "Analiza una decisión desde seis perspectivas, una a la vez.",
        "best_for": "Evaluar una idea en equipo sin mezclar los puntos de vista.", "time": "25–35 min",
    },
    {
        "id": "brainstorming", "name": "Brainstorming y variantes", "code": "BR", "color": "#F59F00", "text_on": "dark",
        "category": "tecnica", "orientation": "Generación abierta y rápida de ideas",
        "tagline": "Genera muchas ideas rápido, sin juicio prematuro.",
        "best_for": "La fase de generación abierta de ideas, solo o en grupo.", "time": "15–30 min",
    },
]


def method_by_id(method_id):
    for m in METHODS:
        if m["id"] == method_id:
            return m
    return None


GOALS = [
    {"label": "Mejorar algo que ya existe: un producto, servicio o proceso", "id": "scamper"},
    {"label": "Explorar un problema centrado en las personas, desde cero", "id": "design-thinking"},
    {"label": "Poner orden en un proceso de diseño o gestión de proyecto", "id": "double-diamond"},
    {"label": "Resolver un bloqueo o problema abstracto, sin quedarte solo en lo lógico", "id": "cps"},
    {"label": "Resolver un problema técnico con un trade-off o contradicción claros", "id": "triz"},
    {"label": "Anticipar riesgos, tendencias o escenarios futuros antes de decidir", "id": "foresight"},
    {"label": "Evaluar una decisión en equipo desde varios ángulos", "id": "six-hats"},
    {"label": "Generar muchas ideas rápido, solo o en equipo", "id": "brainstorming"},
]

SCAMPER_STEPS = [
    {"key": "S", "title": "Sustituir", "prompts": [
        "¿Qué material, componente, persona o regla podrías sustituir?",
        "¿Qué pasaría si cambiaras el lugar, el momento o el proveedor?"]},
    {"key": "C", "title": "Combinar", "prompts": [
        "¿Qué partes, funciones o ideas podrías combinar entre sí?",
        "¿Qué pasaría si unieras esto con algo de otro contexto?"]},
    {"key": "A", "title": "Adaptar", "prompts": [
        "¿Qué otra idea o solución existente podrías adaptar aquí?",
        "¿A qué se parece esto? ¿Qué podrías tomar prestado?"]},
    {"key": "M", "title": "Modificar / Magnificar", "prompts": [
        "¿Qué pasaría si agrandas, achicas o cambias la forma?",
        "¿Qué atributo podrías exagerar o minimizar?"]},
    {"key": "P", "title": "Poner en otro uso", "prompts": [
        "¿Cómo podrías usar esto para un propósito distinto al original?",
        "¿Quién más podría beneficiarse de esto, y para qué?"]},
    {"key": "E", "title": "Eliminar", "prompts": [
        "¿Qué parte podrías quitar, simplificar o reducir al mínimo?",
        "¿Qué pasaría si eliminas una regla o un paso por completo?"]},
    {"key": "R", "title": "Reordenar / Revertir", "prompts": [
        "¿Qué pasaría si inviertes el orden o la causa y el efecto?",
        "¿Qué pasaría si le das la vuelta por completo?"]},
]

DT_LABELS = ["Empatizar", "Definir", "Idear", "Prototipar", "Testear"]
DD_LABELS = ["Descubrir", "Definir", "Desarrollar", "Entregar"]
CPS_LABELS = ["Clarificar", "Idear", "Desarrollar", "Implementar"]
TRIZ_LABELS = ["Introducción", "Contradicción", "Principios"]

SIX_HATS = [
    {"key": "white", "name": "Blanco", "label": "Hechos y datos", "color": "#F4F4F0", "prompts": [
        "¿Qué información objetiva tenemos sobre esto?", "¿Qué datos nos faltan y cómo los conseguimos?"]},
    {"key": "red", "name": "Rojo", "label": "Emociones e intuición", "color": "#D6524A", "prompts": [
        "¿Qué sientes respecto a esto, sin necesidad de justificarlo?", "¿Cuál es tu primera reacción, buena o mala?"]},
    {"key": "black", "name": "Negro", "label": "Precaución y juicio crítico", "color": "#2B2B2E", "prompts": [
        "¿Qué riesgos, debilidades o fallas ves en esto?", "¿Por qué podría no funcionar?"]},
    {"key": "yellow", "name": "Amarillo", "label": "Optimismo y beneficios", "color": "#E0AC2E", "prompts": [
        "¿Qué beneficios u oportunidades hay aquí?", "¿Por qué vale la pena intentarlo?"]},
    {"key": "green", "name": "Verde", "label": "Creatividad y alternativas", "color": "#4C9A5B", "prompts": [
        "¿Qué otras ideas o enfoques son posibles?", "¿Cómo lo resolverías si no hubiera límites?"]},
    {"key": "blue", "name": "Azul", "label": "Proceso y próximos pasos", "color": "#3158C4", "prompts": [
        "¿Qué concluimos después de ver las otras cinco perspectivas?", "¿Cuáles son los próximos pasos concretos?"]},
]

BRAIN_RULES = [
    "No critiques ni evalúes ninguna idea todavía: eso viene después.",
    "Ideas alocadas son bienvenidas — es más fácil suavizar una idea grande que agrandar una tímida.",
    "Prioriza la cantidad: entre más ideas generes, más probable es encontrar una buena.",
    "Combina y mejora: construye sobre las ideas de otros (o las tuyas) en vez de descartarlas.",
]

BRAIN_MODES = [
    {"id": "classic", "name": "Clásico", "desc": "Reglas de Osborn + captura libre de ideas, con temporizador opcional."},
    {"id": "brainwriting", "name": "Brainwriting 6-3-5", "desc": "3 ideas por ronda, construyendo sobre lo anterior, durante 5 rondas."},
    {"id": "mindmap", "name": "Mapa mental", "desc": "Ramifica tu problema en temas principales y anota ideas bajo cada uno."},
]

FORESIGHT_MODES = [
    {"id": "scenarios", "name": "Tendencias + Escenarios", "desc": "Escanea señales de cambio, identifica las fuerzas más inciertas y construye 2-4 futuros posibles para tu reto."},
    {"id": "backcasting", "name": "Backcasting", "desc": "Define el futuro deseado en unos años y traza el camino hacia atrás: qué hitos y acciones te llevan ahí."},
    {"id": "pestel", "name": "PESTEL", "desc": "Mapea el entorno externo de tu reto en 6 ángulos: Político, Económico, Social, Tecnológico, Ecológico, Legal."},
]

FORESIGHT_SCENARIOS_LABELS = ["Señales", "Fuerzas motrices", "Escenarios", "Implicaciones"]
FORESIGHT_BACKCAST_LABELS = ["Futuro deseado", "Hitos", "Obstáculos", "Acciones ahora"]

PESTEL_CATEGORIES = [
    {"key": "politico", "name": "Político", "color": "#7048E8", "prompts": [
        "¿Qué leyes, regulaciones o decisiones de gobierno podrían afectar esto?",
        "¿Hay cambios políticos o de política pública en el horizonte?"]},
    {"key": "economico", "name": "Económico", "color": "#0CA678", "prompts": [
        "¿Qué pasa con costos, inflación, tipo de cambio o poder adquisitivo?",
        "¿Cómo te afecta un escenario de crecimiento vs. uno de recesión?"]},
    {"key": "social", "name": "Social", "color": "#D6336C", "prompts": [
        "¿Qué cambios en hábitos, valores o demografía son relevantes?",
        "¿Cómo está cambiando lo que las personas esperan o valoran?"]},
    {"key": "tecnologico", "name": "Tecnológico", "color": "#3B5BDB", "prompts": [
        "¿Qué tecnología emergente podría volver esto obsoleto o abrir una oportunidad?",
        "¿Qué tan rápido está cambiando la tecnología en este espacio?"]},
    {"key": "ecologico", "name": "Ecológico", "color": "#2F9E44", "prompts": [
        "¿Qué impacto ambiental tiene esto, o qué presión de sostenibilidad enfrenta?",
        "¿Hay riesgos climáticos o de recursos naturales a considerar?"]},
    {"key": "legal", "name": "Legal", "color": "#495057", "prompts": [
        "¿Qué normas, permisos o riesgos legales aplican?",
        "¿Qué podría cambiar en el marco legal que te afecte?"]},
]

TRIZ_PRINCIPLES = [
    (1, "Segmentación", "Divide el objeto o sistema en partes independientes o fáciles de ensamblar y desmontar."),
    (2, "Extracción", "Separa la parte o propiedad \"molesta\" (o la única necesaria) del resto del sistema."),
    (3, "Calidad local", "Haz que cada parte cumpla la función más adecuada para su condición particular, en vez de una uniforme."),
    (4, "Asimetría", "Cambia una forma simétrica por una asimétrica cuando eso resuelve mejor el problema."),
    (5, "Combinación", "Une en el espacio o el tiempo operaciones, objetos o funciones similares o relacionadas."),
    (6, "Universalidad", "Haz que una parte cumpla varias funciones, eliminando la necesidad de otras partes."),
    (7, "Anidado", "Coloca un objeto dentro de otro, y ese dentro de un tercero, como muñecas rusas."),
    (8, "Contrapeso", "Compensa el peso o efecto de un objeto combinándolo con otro que genere una fuerza opuesta."),
    (9, "Contraacción previa", "Aplica de antemano una acción opuesta para contrarrestar efectos no deseados futuros."),
    (10, "Acción previa", "Realiza el cambio necesario, total o parcialmente, antes de que se necesite."),
    (11, "Compensación previa", "Prepara medios de emergencia con anticipación para compensar la baja fiabilidad de un objeto."),
    (12, "Equipotencialidad", "Rediseña el entorno para que no haga falta subir o bajar un objeto, ahorrando ese esfuerzo."),
    (13, "Inversión", "Haz lo contrario de lo habitual: invierte la acción, el objeto o el proceso."),
    (14, "Curvatura", "Reemplaza partes o superficies rectas por curvas; usa rodillos, esferas o espirales."),
    (15, "Dinamismo", "Permite que el objeto o su entorno se ajusten automáticamente en cada etapa de uso."),
    (16, "Acción parcial o excesiva", "Si es difícil lograr el 100% del efecto, apunta a un poco más o un poco menos."),
    (17, "Cambio de dimensión", "Mueve el objeto o proceso a dos o tres dimensiones, o cambia su orientación."),
    (18, "Vibración mecánica", "Haz que el objeto vibre u oscile para producir el efecto deseado."),
    (19, "Acción periódica", "Reemplaza una acción continua por una periódica o pulsante."),
    (20, "Continuidad de la acción útil", "Elimina las pausas y el trabajo en vacío; que todas las partes trabajen a su máxima carga."),
    (21, "Apresuramiento", "Realiza un proceso dañino o riesgoso muy rápido para minimizar su efecto negativo."),
    (22, "Convertir lo dañino en beneficio", "Usa factores nocivos del entorno para lograr un efecto positivo."),
    (23, "Retroalimentación", "Introduce retroalimentación para mejorar un proceso o acción; ajústala si ya existe."),
    (24, "Mediación", "Usa un objeto o proceso intermedio para transferir o realizar una acción."),
    (25, "Autoservicio", "Haz que el objeto se sirva a sí mismo, realizando funciones de mantenimiento o reparación."),
    (26, "Copiado", "Usa una copia simple o barata en lugar de un objeto complejo, caro o frágil."),
    (27, "Objetos de vida corta", "Reemplaza un objeto caro y duradero por varios baratos y desechables."),
    (28, "Sustitución de sistema mecánico", "Cambia un sistema mecánico por uno óptico, acústico, térmico u olfativo."),
    (29, "Sistemas neumáticos o hidráulicos", "Reemplaza partes sólidas por gases o líquidos: infla, presuriza o usa hidráulica."),
    (30, "Películas flexibles o membranas", "Usa cubiertas y películas delgadas y flexibles en vez de estructuras rígidas."),
    (31, "Materiales porosos", "Haz que el objeto sea poroso o agrégale elementos porosos para nuevas funciones."),
    (32, "Cambio de color", "Cambia el color o la transparencia del objeto o su entorno para facilitar su uso."),
    (33, "Homogeneidad", "Haz que los objetos que interactúan sean del mismo material o tengan propiedades similares."),
    (34, "Descarte y regeneración", "Haz que una parte se descarte o transforme al cumplir su función."),
    (35, "Transformación de propiedades", "Cambia el estado físico, la concentración, la flexibilidad o la temperatura del objeto."),
    (36, "Transición de fase", "Aprovecha los fenómenos que ocurren durante un cambio de fase, por ejemplo de sólido a líquido."),
    (37, "Expansión térmica", "Usa la expansión o contracción térmica de los materiales para generar un efecto."),
    (38, "Uso de oxidantes", "Reemplaza aire normal por aire enriquecido, oxígeno puro o ambientes ionizados para acelerar un proceso."),
    (39, "Atmósfera inerte", "Reemplaza un entorno normal por uno inerte o neutro para evitar reacciones no deseadas."),
    (40, "Materiales compuestos", "Reemplaza un material homogéneo por uno compuesto, combinando propiedades de varios."),
]
