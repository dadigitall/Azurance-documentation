# Skill : Audit BFF ↔ Documentation OpenAPI/MDX

## Description

Vérifie que la documentation publique (OpenAPI + pages MDX + navigation `docs.json`) est alignée avec les routes, DTOs et transformations réelles des BFFs NestJS du projet Azurance. Identifie les écarts et guide leur correction.

## Quand utiliser ce skill

- Après une évolution des BFFs (nouvelle route, nouveau DTO, changement de scope).
- Avant une release de documentation pour valider la cohérence.
- Quand on soupçonne qu'une page MDX ou un contrat OpenAPI est désynchronisé du BFF réel.

## Principe directeur

**Les docs suivent le BFF réel.** En cas de divergence, c'est le code BFF qui fait foi. Ne jamais inventer un contrat non implémenté.

## Comment lancer l'audit

### 1. Audit complet (tous les BFFs)

```bash
python3 .devin/skills/audit-bff-docs/audit_bff_docs.py
```

### 2. Audit ciblé (un seul BFF)

```bash
python3 .devin/skills/audit-bff-docs/audit_bff_docs.py --bff provider-api-bff
python3 .devin/skills/audit-bff-docs/audit_bff_docs.py --bff insurer-bff
```

### 3. Audit avec détails DTOs

```bash
python3 .devin/skills/audit-bff-docs/audit_bff_docs.py --dto
```

## Ce que le script vérifie

1. **Routes BFF ↔ OpenAPI** : chaque route définie dans un controller NestJS doit exister dans le fichier OpenAPI correspondant, et inversement.
2. **OpenAPI ↔ MDX** : chaque route OpenAPI doit avoir au moins une page MDX qui la référence, et inversement.
3. **Pages MDX ↔ docs.json** : chaque page MDX dans `erp-*/api/` doit être référencée dans `docs.json`.
4. **Validité YAML/JSON** : les fichiers OpenAPI doivent parser, `docs.json` doit être du JSON valide.
5. **Blocs JSON MDX** : tous les blocs ```json dans les pages MDX doivent être du JSON valide.
6. **Scopes BFF ↔ OpenAPI** : les scopes documentés dans OpenAPI doivent correspondre à ceux du `ApiKeyGuard`.

## BFFs supportés

| BFF | Dossier source | OpenAPI | Pages MDX |
|-----|---------------|---------|-----------|
| `provider-api-bff` | `services/gateway-service/bffs/provider-api-bff/src` | `openapi/provider-api.openapi.yml` | `erp-prestataires/api/` |
| `insurer-bff` | `services/gateway-service/bffs/insurer-bff/src` | `openapi/insurer-api.openapi.yml` | `erp-assurances/api/` |

## Workflow de correction

Quand le script identifie des écarts :

1. **Route BFF manquante dans OpenAPI** → ajouter le path + operation dans le fichier OpenAPI correspondant.
2. **Route OpenAPI non exposée par le BFF** → retirer de l'OpenAPI (sauf si route globale Nest non-controller).
3. **Route OpenAPI sans page MDX** → créer une page MDX dans le dossier `api/` approprié.
4. **Page MDX non référencée dans docs.json** → ajouter dans la navigation `docs.json`.
5. **Écart de scope** → corriger le scope documenté dans OpenAPI et/ou MDX selon le `ApiKeyGuard`.
6. **Écart de paramètre** → aligner le nom du paramètre de chemin entre OpenAPI, MDX et BFF.
7. **Écart de DTO** → aligner les champs, types, enums et validations entre le DTO BFF, le schéma OpenAPI et la table MDX.

## Règles de rédaction

- Langue : français.
- Conserver le frontmatter existant (`title`, `description`, `icon`).
- Utiliser des identifiants sandbox clairement reconnaissables (`*_sandbox_*`).
- Ne jamais documenter `tenant_id`, `provider_uuid`, `insurer_uid` dans les requêtes publiques (dérivés de `X-Api-Key`).
- Ne jamais exposer d'ID numérique SQL dans les exemples de réponse.
- Ajouter une entrée au `changelog.mdx` pour toute évolution publique.

## Fichiers du skill

- `audit_bff_docs.py` : script d'audit automatisé.
- `SKILL.md` : ce fichier (instructions).
