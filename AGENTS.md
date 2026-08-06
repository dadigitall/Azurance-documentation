# Instructions pour les agents

## Contexte du projet

Ce dépôt contient la documentation publique Mintlify d'Azurance. Il ne contient pas l'implémentation des APIs : les contrats publics sont décrits dans `openapi/` et les guides sont écrits en MDX.

Les deux produits documentés sont :

- **ERP Prestataires** : intégrations pour hôpitaux, cliniques, pharmacies et laboratoires.
- **ERP Assurances** : intégrations pour assureurs, mutuelles et gestionnaires de portefeuilles santé.

La documentation est principalement rédigée en français. Conserver cette langue, le vocabulaire métier existant et le ton direct des pages actuelles.

## Sources de vérité

Lire avant toute modification importante :

- `docs.json` pour la navigation, le thème et les options Mintlify ;
- `index.mdx` pour le positionnement général et les domaines officiels ;
- `commun/authentification.mdx` pour l'authentification ;
- `commun/securite-scopes-webhooks.mdx` pour les règles de sécurité et les scopes ;
- le quickstart du produit concerné ;
- le fichier OpenAPI correspondant dans `openapi/`.

En cas de divergence, ne pas inventer un contrat. Vérifier les pages liées et mettre à jour toutes les sources concernées de manière cohérente.

## Organisation des fichiers

- `commun/` contient les règles partagées par les deux produits.
- `erp-prestataires/` contient les guides et la référence de l'API prestataire.
- `erp-assurances/` contient les guides et la référence de l'API assureur.
- `openapi/` contient les contrats OpenAPI v3 utilisés par les pages de référence.
- `docs.json` référence explicitement les pages visibles dans la navigation.
- `style.css` contient les personnalisations visuelles globales.

## Règles de rédaction MDX

- Conserver le frontmatter existant (`title`, `description`, et `icon` lorsque la page en utilise un).
- Utiliser le format MDX attendu par Mintlify et respecter le style des pages voisines.
- Employer des exemples réalistes mais fictifs, avec des identifiants sandbox clairement reconnaissables.
- Garder les exemples synchronisés entre les guides, les pages d'endpoint et les schémas OpenAPI.
- Ajouter une page à `docs.json` si elle doit apparaître dans la navigation.
- Vérifier les liens relatifs et les chemins OpenAPI après tout déplacement ou renommage.
- Mettre à jour `changelog.mdx` pour toute évolution de contrat public, de workflow ou de navigation importante.
- Ne pas ajouter de commentaires ou de contenu hors sujet dans les pages.

## Règles API et sécurité

- Utiliser uniquement les domaines publics documentés :
  - `https://provider-api-sandbox.elenami.com` et `https://provider-api.elenami.com` ;
  - `https://insurer-api-sandbox.elenami.com` et `https://insurer-api.elenami.com`.
- Documenter l'authentification partenaire avec `X-Api-Key`.
- Utiliser `X-Request-Id` pour la corrélation et `Idempotency-Key` lorsque l'opération le prévoit.
- Ne jamais documenter, générer ou journaliser une clé API réelle.
- Ne jamais conseiller d'appeler les APIs depuis un frontend ou une application mobile.
- Ne pas demander dans les requêtes publiques `tenant_id`, `provider_uuid`, `insurer_uid` ou tout autre contexte dérivé de la clé lorsque l'API le déduit déjà.
- Respecter la séparation stricte des clés et des URLs sandbox/production.
- Ne documenter que les champs, scopes, statuts et valeurs `enum` présents dans le contrat public.
- Pour les retries, conserver la règle existante : réessayer uniquement les réponses `429` et `5xx`, avec backoff.

## Modification d'un endpoint

Pour ajouter ou modifier un endpoint :

1. Mettre à jour le contrat OpenAPI approprié dans `openapi/`.
2. Vérifier le `operationId`, la méthode, le chemin, les paramètres, le body, les réponses et les erreurs.
3. Mettre à jour ou créer la page MDX correspondante dans le dossier `api/`.
4. Actualiser le quickstart ou le guide métier lorsque le parcours change.
5. Vérifier les scopes, l'idempotence, les headers, les exemples et les règles de sécurité.
6. Ajouter la page dans `docs.json` si nécessaire.
7. Ajouter une entrée au changelog pour une évolution publique.

## Vérifications locales

Le dépôt ne contient actuellement ni `package.json`, ni suite de tests automatisée. Effectuer au minimum :

```bash
git diff --check
python3 -m json.tool docs.json >/dev/null
```

Pour une modification MDX ou de navigation, lancer la prévisualisation Mintlify depuis la racine :

```bash
npx mint dev
```

Contrôler les pages impactées, les erreurs de rendu, les liens, les blocs OpenAPI et les exemples générés. Pour les contrats YAML, utiliser un parseur YAML disponible dans l'environnement afin de vérifier leur validité syntaxique.

## Workflow Git

- Ne pas modifier les changements de travail existants qui ne sont pas liés à la tâche.
- Ne pas réécrire l'historique, forcer un push ou supprimer des fichiers sans demande explicite.
- Ne pas committer de secrets, de clés API ou de données personnelles réelles.
- Utiliser des messages de commit courts et descriptifs, sans co-auteur ni signature d'outil.
