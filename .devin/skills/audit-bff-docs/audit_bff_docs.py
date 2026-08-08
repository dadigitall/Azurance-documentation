#!/usr/bin/env python3
"""
Audit BFF ↔ OpenAPI ↔ MDX pour la documentation Azurance.

Vérifie que les routes définies dans les controllers NestJS des BFFs
sont alignées avec les fichiers OpenAPI, les pages MDX et la navigation docs.json.

Usage:
    python3 audit_bff_docs.py                    # audit tous les BFFs
    python3 audit_bff_docs.py --bff provider-api-bff
    python3 audit_bff_docs.py --bff insurer-bff
    python3 audit_bff_docs.py --dto              # inclut l'analyse des DTOs
    python3 audit_bff_docs.py --json-blocks      # valide les blocs JSON des MDX
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERREUR: PyYAML non installé. Installer avec: pip3 install pyyaml")
    sys.exit(1)

# ─── Configuration ───────────────────────────────────────────────────────────

AZURANCE_ROOT = Path("/var/www/html/azurance")
DOCS_ROOT = Path("/var/www/html/Azurance-documentation")
BFFS_ROOT = AZURANCE_ROOT / "services" / "gateway-service" / "bffs"

BFF_CONFIG = {
    "provider-api-bff": {
        "src": BFFS_ROOT / "provider-api-bff" / "src",
        "openapi": DOCS_ROOT / "openapi" / "provider-api.openapi.yml",
        "mdx_dir": DOCS_ROOT / "erp-prestataires" / "api",
        "openapi_ref": "provider-api.openapi.yml",
        "label": "ERP Prestataires",
    },
    "insurer-bff": {
        "src": BFFS_ROOT / "insurer-bff" / "src",
        "openapi": DOCS_ROOT / "openapi" / "insurer-api.openapi.yml",
        "mdx_dir": DOCS_ROOT / "erp-assurances" / "api",
        "openapi_ref": "insurer-api.openapi.yml",
        "label": "ERP Assurances",
    },
}

HTTP_METHODS = ["get", "post", "put", "patch", "delete"]


# ─── Extraction des routes BFF ───────────────────────────────────────────────

def extract_bff_routes(src_dir: Path) -> list[tuple[str, str, str]]:
    """Extrait toutes les routes des controllers NestJS.
    Retourne [(method, path, controller_file), ...]
    """
    routes = []
    for f in sorted(src_dir.rglob("*.controller.ts")):
        content = f.read_text()
        base_match = re.search(r"@Controller\('([^']*)'\)", content)
        base = base_match.group(1) if base_match else ""

        for m in re.finditer(
            r"@(Get|Post|Put|Patch|Delete)\((?:'([^']*)')?\)", content
        ):
            method, path = m.groups()
            path = path or ""
            full = "/" + "/".join(
                p.strip("/") for p in [base, path] if p.strip("/")
            )
            full = re.sub(r":([A-Za-z0-9_]+)", r"{\1}", full)
            routes.append((method.upper(), full, str(f.relative_to(src_dir))))

    return routes


# ─── Extraction des routes OpenAPI ───────────────────────────────────────────

def extract_openapi_routes(openapi_path: Path) -> list[tuple[str, str]]:
    """Extrait les routes du fichier OpenAPI.
    Retourne [(method_upper, path), ...]
    """
    spec = yaml.safe_load(openapi_path.read_text())
    routes = []
    for path, ops in spec.get("paths", {}).items():
        for method in HTTP_METHODS:
            if method in ops:
                routes.append((method.upper(), path))
    return routes


# ─── Extraction des routes référencées dans les MDX ──────────────────────────

def extract_mdx_routes(mdx_dir: Path, openapi_ref: str) -> list[tuple[str, str, str]]:
    """Extrait les références OpenAPI des pages MDX.
    Retourne [(method_upper, path, file), ...]
    """
    pattern = re.compile(
        rf'openapi:\s*"/openapi/{re.escape(openapi_ref)}\s+'
        r'(GET|POST|PUT|PATCH|DELETE)\s+([^"]+)"'
    )
    routes = []
    for f in sorted(mdx_dir.glob("*.mdx")):
        content = f.read_text()
        m = pattern.search(content)
        if m:
            routes.append((m.group(1), m.group(2), str(f.relative_to(DOCS_ROOT))))
    return routes


# ─── Vérification docs.json ──────────────────────────────────────────────────

def check_docs_json_references(mdx_dir: Path) -> list[str]:
    """Vérifie que toutes les pages MDX sont référencées dans docs.json."""
    docs_json = json.loads((DOCS_ROOT / "docs.json").read_text())
    docs_content = (DOCS_ROOT / "docs.json").read_text()

    missing = []
    for f in sorted(mdx_dir.glob("*.mdx")):
        ref = str(f.relative_to(DOCS_ROOT)).replace(".mdx", "")
        if ref not in docs_content:
            missing.append(ref)
    return missing


# ─── Validation des blocs JSON dans les MDX ──────────────────────────────────

def validate_mdx_json_blocks(mdx_dir: Path) -> list[tuple[str, str]]:
    """Valide tous les blocs ```json dans les pages MDX.
    Retourne [(file, error), ...] pour les blocs invalides.
    """
    errors = []
    for f in sorted(mdx_dir.glob("*.mdx")):
        content = f.read_text()
        blocks = re.findall(r"```json\n(.*?)```", content, re.S)
        for i, block in enumerate(blocks, 1):
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                errors.append((str(f.relative_to(DOCS_ROOT)), f"bloc {i}: {e}"))
    return errors


# ─── Extraction des scopes BFF ───────────────────────────────────────────────

def extract_bff_scopes(src_dir: Path) -> dict[str, str]:
    """Extrait les mappings de scopes du ApiKeyGuard.
    Retourne {path_pattern: scope}
    """
    guard_file = src_dir / "common" / "guards" / "api-key.guard.ts"
    if not guard_file.exists():
        return {}

    content = guard_file.read_text()
    scopes = {}
    # Cherche les patterns return ['scope']
    for m in re.finditer(
        r"if \(path\.includes\('([^']+)'\).*?\n\s+return \['([^']+)'\];",
        content,
        re.S,
    ):
        scopes[m.group(1)] = m.group(2)
    return scopes


# ─── Rapport ─────────────────────────────────────────────────────────────────

def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def audit_bff(bff_name: str, config: dict, check_dto: bool = False, check_json: bool = False):
    """Audit un BFF spécifique."""
    label = config["label"]
    src = config["src"]
    openapi_path = config["openapi"]
    mdx_dir = config["mdx_dir"]
    openapi_ref = config["openapi_ref"]

    print_section(f"AUDIT {label} ({bff_name})")

    # ── Vérifier l'existence des fichiers
    if not src.exists():
        print(f"  ❌ Dossier BFF introuvable: {src}")
        return False
    if not openapi_path.exists():
        print(f"  ❌ Fichier OpenAPI introuvable: {openapi_path}")
        return False
    if not mdx_dir.exists():
        print(f"  ❌ Dossier MDX introuvable: {mdx_dir}")
        return False

    all_ok = True

    # ── 1. Routes BFF
    bff_routes = extract_bff_routes(src)
    print(f"\n  Routes BFF trouvées: {len(bff_routes)}")

    # ── 2. Routes OpenAPI
    try:
        openapi_routes = extract_openapi_routes(openapi_path)
        print(f"  Routes OpenAPI trouvées: {len(openapi_routes)}")
    except Exception as e:
        print(f"  ❌ Erreur parsing OpenAPI: {e}")
        return False

    # ── 3. Routes MDX
    mdx_routes = extract_mdx_routes(mdx_dir, openapi_ref)
    print(f"  Pages MDX trouvées: {len(mdx_routes)}")

    # ── 4. Comparaison BFF ↔ OpenAPI
    bff_set = {(m, p) for m, p, _ in bff_routes}
    openapi_set = set(openapi_routes)

    openapi_only = sorted(openapi_set - bff_set)
    bff_only = sorted(bff_set - openapi_set)

    if openapi_only:
        print(f"\n  ⚠️  Routes dans OpenAPI mais PAS dans le BFF ({len(openapi_only)}):")
        for method, path in openapi_only:
            print(f"     {method:6s} {path}")
        all_ok = False
    else:
        print(f"\n  ✅ Aucune route OpenAPI orpheline")

    if bff_only:
        print(f"\n  ⚠️  Routes dans le BFF mais PAS dans OpenAPI ({len(bff_only)}):")
        for method, path in bff_only:
            print(f"     {method:6s} {path}")
        all_ok = False
    else:
        print(f"  ✅ Aucune route BFF manquante dans OpenAPI")

    # ── 5. Comparaison OpenAPI ↔ MDX
    mdx_set = {(m, p) for m, p, _ in mdx_routes}

    openapi_no_mdx = sorted(openapi_set - mdx_set)
    mdx_no_openapi = sorted(mdx_set - openapi_set)

    if openapi_no_mdx:
        print(f"\n  ⚠️  Routes OpenAPI sans page MDX ({len(openapi_no_mdx)}):")
        for method, path in openapi_no_mdx:
            print(f"     {method:6s} {path}")
        all_ok = False
    else:
        print(f"\n  ✅ Toutes les routes OpenAPI ont une page MDX")

    if mdx_no_openapi:
        print(f"\n  ⚠️  Pages MDX référençant une route absente de l'OpenAPI ({len(mdx_no_openapi)}):")
        for method, path in mdx_no_openapi:
            print(f"     {method:6s} {path}")
        all_ok = False
    else:
        print(f"  ✅ Toutes les pages MDX référencent une route OpenAPI valide")

    # ── 6. Vérification docs.json
    missing_in_docs = check_docs_json_references(mdx_dir)
    if missing_in_docs:
        print(f"\n  ⚠️  Pages MDX non référencées dans docs.json ({len(missing_in_docs)}):")
        for ref in missing_in_docs:
            print(f"     {ref}")
        all_ok = False
    else:
        print(f"\n  ✅ Toutes les pages MDX sont dans docs.json")

    # ── 7. Validation des blocs JSON
    if check_json:
        json_errors = validate_mdx_json_blocks(mdx_dir)
        if json_errors:
            print(f"\n  ⚠️  Blocs JSON invalides dans les MDX ({len(json_errors)}):")
            for f, err in json_errors:
                print(f"     {f}: {err}")
            all_ok = False
        else:
            print(f"\n  ✅ Tous les blocs JSON des MDX sont valides")

    # ── 8. Scopes BFF
    scopes = extract_bff_scopes(src)
    if scopes:
        print(f"\n  Scopes BFF configurés ({len(scopes)}):")
        for pattern, scope in sorted(scopes.items()):
            print(f"     {pattern:40s} → {scope}")

    # ── 9. DTOs (optionnel)
    if check_dto:
        dto_files = sorted(src.rglob("*.dto.ts"))
        print(f"\n  DTOs trouvés: {len(dto_files)}")
        for f in dto_files:
            print(f"     {f.relative_to(src)}")

    # ── Résumé
    print_section(f"RÉSUMÉ {label}")
    if all_ok:
        print("  ✅ Aucun écart détecté. Documentation alignée avec le BFF.")
    else:
        print("  ❌ Des écarts ont été détectés. Voir les détails ci-dessus.")

    return all_ok


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Audit BFF ↔ OpenAPI ↔ MDX pour Azurance"
    )
    parser.add_argument(
        "--bff",
        choices=list(BFF_CONFIG.keys()),
        help="Auditer un BFF spécifique",
    )
    parser.add_argument(
        "--dto",
        action="store_true",
        help="Inclure l'analyse des DTOs",
    )
    parser.add_argument(
        "--json-blocks",
        action="store_true",
        help="Valider les blocs JSON des pages MDX",
    )
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  AUDIT BFF ↔ DOCUMENTATION AZURANCE")
    print("=" * 70)
    print(f"  BFFs root : {BFFS_ROOT}")
    print(f"  Docs root : {DOCS_ROOT}")

    # Valider docs.json
    try:
        json.loads((DOCS_ROOT / "docs.json").read_text())
        print("  docs.json : ✅ JSON valide")
    except Exception as e:
        print(f"  docs.json : ❌ {e}")

    # Valider OpenAPI YAML
    for name, config in BFF_CONFIG.items():
        try:
            yaml.safe_load(config["openapi"].read_text())
            print(f"  {config['openapi'].name} : ✅ YAML valide")
        except Exception as e:
            print(f"  {config['openapi'].name} : ❌ {e}")

    if args.bff:
        ok = audit_bff(
            args.bff,
            BFF_CONFIG[args.bff],
            check_dto=args.dto,
            check_json=args.json_blocks,
        )
        sys.exit(0 if ok else 1)
    else:
        all_ok = True
        for name, config in BFF_CONFIG.items():
            ok = audit_bff(
                name,
                config,
                check_dto=args.dto,
                check_json=args.json_blocks,
            )
            all_ok = all_ok and ok
        print_section("RÉSUMÉ GLOBAL")
        if all_ok:
            print("  ✅ Tous les BFFs sont alignés avec la documentation.")
        else:
            print("  ❌ Des écarts ont été détectés sur au moins un BFF.")
        sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
