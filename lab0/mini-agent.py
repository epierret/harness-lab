"""Mini-agent : la boucle penser -> outil -> observer, sans framework."""
import subprocess
import ollama

MODELE = "qwen3:8b"

def lire_fichier(chemin: str) -> str:
    """Lit un fichier texte du dépôt (4000 caractères max)."""
    with open(chemin, encoding="utf-8") as f:
        return f.read()[:4000]

def lancer_tests() -> str:
    """Lance pytest et renvoie la fin de la sortie."""
    r = subprocess.run(["pytest", "-q"], capture_output=True, text=True)
    return (r.stdout + r.stderr)[-2000:]

OUTILS = {"lire_fichier": lire_fichier, "lancer_tests": lancer_tests}

messages = [
    {"role": "system", "content": "Tu es un agent de code. Utilise les outils avant de conclure."},
    {"role": "user", "content": "Les tests passent-ils ? Sinon, quel fichier faut-il corriger et pourquoi ?"},
]

for tour in range(6):  # garde-fou : nombre de tours limité
    rep = ollama.chat(model=MODELE, messages=messages, tools=list(OUTILS.values()))
    messages.append(rep.message)
    if not rep.message.tool_calls:
        print("\n✅ Réponse finale :\n", rep.message.content)
        break
    for appel in rep.message.tool_calls:
        resultat = OUTILS[appel.function.name](**(appel.function.arguments or {}))
        print(f"🔧 tour {tour} : {appel.function.name} -> {len(resultat)} caractères")
        messages.append({"role": "tool", "content": resultat, "tool_name": appel.function.name})
