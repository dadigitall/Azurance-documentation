# Documentation Azurance

Documentation publique des intégrations Azurance pour les ERP prestataires et les ERP assurances.

Le site explique comment connecter un hôpital, une clinique, une pharmacie, un laboratoire, un assureur ou une mutuelle aux APIs Azurance, depuis la vérification de la clé API jusqu'au suivi des claims, des remboursements et des webhooks.

## Contenu

- **ERP Prestataires** : éligibilité, personnes couvertes, consentement, parcours clinique, prestations effectuées, documents, claims, facturation, remboursements et webhooks.
- **ERP Assurances** : plans, membres, souscriptions, bénéficiaires, garanties, éligibilité, réseau prestataire, décisions de claims, facturation, analytics et notifications.
- **Documentation commune** : conventions API, authentification, scopes, sécurité, webhooks et erreurs.
- **Référence API** : endpoints documentés à partir des contrats OpenAPI avec exemples `curl`, TypeScript, JavaScript, PHP, Java et C#.
- **Azurance LLM Kit** : contexte Markdown et OpenAPI destiné aux assistants de code.

## Démarrage rapide

Consulter les parcours suivants :

- [Quickstart ERP Prestataires](erp-prestataires/quickstart.mdx)
- [Quickstart ERP Assurances](erp-assurances/quickstart.mdx)
- [Authentification](commun/authentification.mdx)
- [Sécurité, scopes et webhooks](commun/securite-scopes-webhooks.mdx)
- [Conventions API](commun/conventions-api.mdx)
- [Gestion des erreurs](commun/erreurs.mdx)

## Environnements API

Les clés sandbox et production sont strictement séparées.

| Espace | Sandbox | Production |
| --- | --- | --- |
| ERP Prestataires | `https://provider-api-sandbox.elenami.com` | `https://provider-api.elenami.com` |
| ERP Assurances | `https://insurer-api-sandbox.elenami.com` | `https://insurer-api.elenami.com` |

Les appels utilisent le header public `X-Api-Key`. Les clés doivent rester côté serveur, dans un coffre de secrets ou dans les variables d'environnement du middleware/ERP. Elles ne doivent jamais être exposées dans un frontend, une application mobile ou des logs.

## Structure du dépôt

```text
.
├── assets/                  # Logos et icônes de la documentation
├── commun/                  # Conventions, sécurité, erreurs et authentification
├── erp-prestataires/        # Guides et endpoints pour les prestataires
│   └── api/                 # Pages générées depuis le contrat prestataire
├── erp-assurances/          # Guides et endpoints pour les assureurs
│   └── api/                 # Pages générées depuis le contrat assureur
├── openapi/                 # Contrats OpenAPI v3 des APIs publiques
├── changelog.mdx            # Historique des évolutions documentaires
├── docs.json                # Configuration Mintlify et navigation du site
├── index.mdx                # Page d'accueil
├── style.css                # Personnalisation visuelle
├── AGENTS.md                # Instructions pour les assistants de code
└── README.md                # Présentation du projet
```

## Prévisualiser la documentation

Ce dépôt ne contient pas de `package.json` : la documentation est configurée directement pour Mintlify. Avec le CLI Mintlify disponible, lancer depuis la racine du dépôt :

```bash
npx mint dev
```

Le CLI démarre une prévisualisation locale et recharge les pages pendant leur modification. La publication dépend de la configuration du projet Mintlify et n'est pas définie par un script local dans ce dépôt.

## Contrats OpenAPI

Les contrats disponibles sont :

- [`openapi/provider-api.openapi.yml`](openapi/provider-api.openapi.yml)
- [`openapi/insurer-api.openapi.yml`](openapi/insurer-api.openapi.yml)

Les pages de référence API utilisent ces fichiers via les blocs `openapi` de Mintlify. Toute modification d'un endpoint public doit conserver la cohérence entre le contrat OpenAPI, les exemples de guides et la navigation définie dans `docs.json`.

## Vérifications recommandées

Avant de proposer une modification :

```bash
git diff --check
python3 -m json.tool docs.json >/dev/null
```

Pour une modification d'un contrat YAML, vérifier également que le fichier reste un YAML valide avec l'outil YAML disponible dans l'environnement, puis ouvrir la prévisualisation Mintlify et contrôler les pages concernées.

## Contribution

1. Créer une branche dédiée.
2. Modifier les pages ou les contrats concernés en suivant les règles de [`AGENTS.md`](AGENTS.md).
3. Vérifier la navigation, les liens relatifs, les exemples et les contrats OpenAPI.
4. Exécuter les vérifications recommandées.
5. Décrire clairement les changements dans la pull request.

Les changements de contrat public ou de parcours doivent également être ajoutés à [`changelog.mdx`](changelog.mdx).

## Licence et statut

Ce dépôt contient la documentation publique d'intégration Azurance. Les exemples utilisent des identifiants sandbox et ne constituent pas des secrets ou des identifiants de production.
