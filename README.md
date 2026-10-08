# GitHub Profile Inspector

Uma integração de linha de comando escrita em Python que consulta a
[API REST oficial do GitHub](https://docs.github.com/rest) e apresenta um resumo
de qualquer perfil público.

## Recursos

- informações públicas do perfil;
- quantidade de seguidores e repositórios;
- linguagens mais utilizadas;
- total de estrelas recebidas;
- lista dos repositórios próprios com mais estrelas;
- saída amigável ou em JSON;
- autenticação opcional por `GITHUB_TOKEN` para ampliar o limite da API.

## Requisitos

- Python 3.10 ou superior;
- conexão com a internet.

O projeto utiliza somente a biblioteca padrão do Python.

## Como usar

Clone o repositório e execute:

```bash
python github_profile_inspector.py Flpvoigt
```

Para receber JSON:

```bash
python github_profile_inspector.py Flpvoigt --json
```

É possível usar um token sem colocá-lo no código:

```bash
export GITHUB_TOKEN="seu_token"
python github_profile_inspector.py Flpvoigt
```

No PowerShell:

```powershell
$env:GITHUB_TOKEN = "seu_token"
python .\github_profile_inspector.py Flpvoigt
```

O token é opcional e nunca deve ser enviado ao repositório.

## Testes

```bash
python -m unittest discover -s tests -v
```

## API utilizada

- `GET /users/{username}`
- `GET /users/{username}/repos`

Consulte a [documentação da API REST](https://docs.github.com/rest/users/users)
para conhecer os limites e formatos das respostas.

## Suporte

Para dúvidas ou problemas, abra uma
[issue](https://github.com/Flpvoigt/github-profile-inspector/issues).

## Licença

Distribuído sob a licença MIT.
