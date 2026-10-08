"""Consulta informações públicas de perfis pela API REST oficial do GitHub."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from typing import Any

API_URL = "https://api.github.com"
USER_AGENT = "github-profile-inspector/1.0"


class GitHubAPIError(RuntimeError):
    """Erro legível devolvido pela integração com o GitHub."""


def api_get(path: str) -> Any:
    """Realiza uma requisição GET autenticada opcionalmente por GITHUB_TOKEN."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(f"{API_URL}{path}", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            raise GitHubAPIError("Usuário não encontrado.") from error
        if error.code == 403:
            raise GitHubAPIError(
                "Limite da API atingido. Defina GITHUB_TOKEN e tente novamente."
            ) from error
        raise GitHubAPIError(f"A API do GitHub respondeu com HTTP {error.code}.") from error
    except urllib.error.URLError as error:
        raise GitHubAPIError("Não foi possível conectar à API do GitHub.") from error


def inspect_profile(username: str) -> dict[str, Any]:
    """Obtém o perfil e resume seus repositórios públicos."""
    safe_username = urllib.parse.quote(username.strip(), safe="")
    if not safe_username:
        raise GitHubAPIError("Informe um usuário do GitHub.")

    profile = api_get(f"/users/{safe_username}")
    repositories = api_get(
        f"/users/{safe_username}/repos?per_page=100&sort=updated&type=owner"
    )
    own_repositories = [repository for repository in repositories if not repository["fork"]]
    languages = Counter(
        repository["language"]
        for repository in own_repositories
        if repository.get("language")
    )
    most_starred = sorted(
        own_repositories,
        key=lambda repository: repository["stargazers_count"],
        reverse=True,
    )[:5]

    return {
        "login": profile["login"],
        "name": profile.get("name"),
        "bio": profile.get("bio"),
        "location": profile.get("location"),
        "url": profile["html_url"],
        "followers": profile["followers"],
        "following": profile["following"],
        "public_repositories": profile["public_repos"],
        "own_repositories_analyzed": len(own_repositories),
        "total_stars": sum(repository["stargazers_count"] for repository in own_repositories),
        "languages": dict(languages.most_common()),
        "most_starred": [
            {
                "name": repository["name"],
                "stars": repository["stargazers_count"],
                "url": repository["html_url"],
            }
            for repository in most_starred
        ],
    }


def format_report(report: dict[str, Any]) -> str:
    """Transforma o relatório em texto amigável para o terminal."""
    languages = ", ".join(
        f"{language} ({count})" for language, count in report["languages"].items()
    ) or "nenhuma identificada"
    repositories = "\n".join(
        f"  - {repository['name']}: {repository['stars']} estrela(s)"
        for repository in report["most_starred"]
    ) or "  - nenhum repositório"

    return "\n".join(
        [
            f"GitHub: {report['login']}",
            f"Nome: {report['name'] or 'não informado'}",
            f"Bio: {report['bio'] or 'não informada'}",
            f"Localização: {report['location'] or 'não informada'}",
            f"Perfil: {report['url']}",
            "",
            f"Seguidores: {report['followers']}",
            f"Seguindo: {report['following']}",
            f"Repositórios públicos: {report['public_repositories']}",
            f"Repositórios próprios analisados: {report['own_repositories_analyzed']}",
            f"Total de estrelas: {report['total_stars']}",
            f"Linguagens: {languages}",
            "",
            "Repositórios com mais estrelas:",
            repositories,
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analisa um perfil público usando a API REST do GitHub."
    )
    parser.add_argument("username", help="nome de usuário no GitHub")
    parser.add_argument("--json", action="store_true", help="exibe a resposta em JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = inspect_profile(args.username)
    except GitHubAPIError as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

