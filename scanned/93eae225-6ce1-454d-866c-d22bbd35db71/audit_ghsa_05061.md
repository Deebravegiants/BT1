# [H] PraisonAI recipe serve Typer command bypasses the non-localhost authentication guard

## Summary
Severity: High
Advisory: GHSA-5qw8-f2g9-ff29
CVE: CVE-2026-56836
CWE: CWE-287, CWE-306, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-5qw8-f2g9-ff29
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=4.5.112 <4.6.59

## Details
# PraisonAI `recipe serve` Typer command bypasses the non-localhost authentication guard

## Summary

PraisonAI's installed console entrypoint is Typer-first. In current releases,
the `recipe` command is registered in the Typer app and
`praisonai recipe serve` dispatches to the deprecated Typer command in
`src/praisonai/praisonai/cli/commands/recipe.py`.

That Typer command can start the Recipe HTTP server on a non-localhost
interface with no authentication:

```text
praisonai recipe serve --host 0.0.0.0 --admin
```

It prints a deprecation warning, then launches the server with:

```json
{
  "host": "0.0.0.0",
  "config": {
    "cors_origins": "*",
    "enable_admin": true
  }
}
```

Because `config.auth` is absent, `create_app()` does not attach the API-key or
JWT middleware. Unauthenticated requests can then reach the recipe API and, when
enabled, `/admin/reload`.

This is an incomplete hardening / sibling-callsite issue. The legacy feature
handler in `src/praisonai/praisonai/cli/features/recipe.py` rejects the same
non-localhost/no-auth combination, and current `create_auth_middleware()` now
fails closed if API-key/JWT auth is selected without a secret. The installed
Typer command bypasses both expectations by never requiring or setting `auth`.

## Affected product

- Repository: `MervinPraison/PraisonAI`
- Package: `praisonai`
- Component:
  - `src/praisonai/praisonai/__main__.py`
  - `src/praisonai/praisonai/cli/app.py`
  - `src/praisonai/praisonai/cli/commands/recipe.py`
  - `src/praisonai/praisonai/cli/features/recipe.py`
  - `src/praisonai/praisonai/recipe/serve.py`

Confirmed affected:

```text
v4.6.58  1ad58ca02975ff1398efeda694ea2ab78f20cf3e
v4.6.57  e90d92231853161ad931f3498da57651a9f8b528
v4.6.56  d3c4a2afadfbf3a3e172e460e607ba4efad263a6
v4.6.34  e5928449f73f66cc8af1de61621aa974ab255133
v4.6.33  dfbb8d78ec7e8dc7118bc722ab1b2524bc98ddab
v4.6.10  4b1b17b963cbd0625e41394a30168c95b26429b2
v4.5.128 b4e3a8a84ade44ac3dd9102b792cdb4311a95937
v4.5.112 bfe3d94bad6db92fc2927c2e3c081ae8303e209e
```

Suggested affected range: `praisonai >= 4.5.112, <= 4.6.58`.

The lower bound is conservative and based on sampled tags. Maintainers should
confirm the exact introduction point before publishing a final range.

## Root cause

The installed entrypoint routes registered Typer commands before falling back
to the legacy dispatcher:

```python
if first_cmd in _get_typer_commands():
    _run_typer(argv)
else:
    _run_legacy(argv)
```

`cli/app.py` registers `commands.recipe` as the `recipe` Typer command:

```python
from .commands.recipe import app as recipe_app
...
app.add_typer(recipe_app, name="recipe", help="Recipe management")
```

The deprecated Typer `recipe serve` implementation accepts a remote host,
defaults CORS to `*`, and only enables authentication when `--api-key` is
explicitly provided:

```python
host: str = typer.Option("127.0.0.1", "--host", "-h", ...)
api_key: str = typer.Option(None, "--api-key", ...)
cors: str = typer.Option("*", "--cors", ...)
admin: bool = typer.Option(False, "--admin", ...)
...
serve_config = {}
...
if api_key:
    serve_config["api_key"] = api_key
    serve_config["auth"] = "api-key"
if cors:
    serve_config["cors_origins"] = cors
if admin:
    serve_config["enable_admin"] = True
...
serve(host=host, port=port, reload=reload, config=serve_config, workers=workers)
```

There is no equivalent to the hardened non-localhost guard in the legacy
feature handler:

```python
if host != "127.0.0.1" and host != "localhost" and auth == "none":
    self._print_error("Auth required for non-localhost binding. Use --auth api-key or --auth jwt")
    return self.EXIT_POLICY_DENIED
```

The Recipe server only installs auth middleware when `config["auth"]` is set:

```python
auth_type = config.get("auth")
if auth_type and auth_type != "none":
    auth_middleware = create_auth_middleware(...)
    if auth_middleware:
        middleware.append(Middleware(auth_middleware))
```

On current `v4.6.58`, the selected-auth paths fail closed correctly:

- `auth=api-key` with no key returns `503`.
- `auth=api-key` with a key but no request header returns `401`.

The vulnerable Typer path does not select auth at all.

## Local-only PoV

Run from the harness checkout:

```bash
uv run \
  --with starlette --with httpx --with typer --with rich --with pyyaml \
  --with sse-starlette --with click --with python-dotenv \
  python submission-bundle/praisonai-prai-cand-016-recipe-serve-typer-auth-bypass/poc/pov_prai_cand_016_recipe_serve_typer_auth_bypass.py \
  --repo artifacts/repos/praisonai-v4.6.58 \
  --label v4.6.58
```

The PoV does not bind a socket. It monkey-patches the recipe server launcher,
invokes the real `praisonai.__main__.main()` entrypoint with
`recipe serve --host 0.0.0.0 --admin`, captures the launch config, and then
uses Starlette's in-process test client to exercise the resulting app.

Observed `v4.6.58` result:

```json
{
  "candidate": "PRAI-CAND-016",
  "entrypoint_exit_code": 0,
  "typer_recipe_command_registered": true,
  "captured_launch": {
    "host": "0.0.0.0",
    "port": 8765,
    "config": {
      "cors_origins": "*",
      "enable_admin": true
    }
  },
  "bypass": {
    "admin_reload": {
      "path": "/admin/reload",
      "status": 200
    },
    "openapi": {
      "path": "/openapi.json",
      "status": 200
    }
  },
  "controls": {
    "auth_api_key_no_secret": {
      "admin_reload": {
        "status": 503
      }
    },
    "auth_api_key_no_header": {
      "admin_reload": {
        "status": 401
      }
    }
  },
  "feature_handler_nonlocalhost_noauth_exit": 4,
  "auth_fail_closed_current_control": true,
  "ok": true
}
```

Stored evidence:

- `evidence/current-v4.6.58.json`
- `evidence/version-sweep.tsv`

## Why this is not intended behavior

This is not only a disagreement about whether operators should configure auth.

PraisonAI's current security documentation says recent hardening changed API
servers so anonymous requests return `401` and servers bind to `127.0.0.1` by
default. Recipe server docs say `auth: api-key` should be used for production,
admin endpoints require auth, and public servers should not run without
authentication.

The implementation also shows the intended boundary:

- `create_auth_middleware()` now returns `503` if API-key/JWT auth is selected
  without a secret.
- `RecipeHandler.cmd_serve()` refuses non-localhost binding when `auth` is
  `none`.
- The vulnerable Typer command is marked deprecated and tells users to use the
  newer command, but the installed entrypoint still routes `praisonai recipe`
  to that Typer command before the legacy handler can enforce the guard.

The official local HTTP sidecar docs describe the sidecar as communicating over
localhost and "no external network required", but the Docker example still uses:

```text
CMD ["praisonai", "recipe", "serve", "--host", "0.0.0.0", "--port", "8765"]
```

That command exposes the Typer path above and does not enable auth, even if
`PRAISONAI_API_KEY` is present in the environment, because this path only sets
`auth` when `--api-key` is passed or a config file sets `auth`.

## Impact

If an operator follows the vulnerable command path on a reachable interface,
any network caller that can reach the Recipe HTTP server can access recipe
runner endpoints without credentials.

Affected endpoints include:

- `GET /v1/recipes`
- `POST /v1/recipes/run`
- `POST /v1/recipes/stream`
- `POST /v1/recipes/validate`
- optional `POST /admin/reload` when admin endpoints are enabled

The exact impact depends on configured recipes and deployment context. At a
minimum, an attacker can enumerate recipes and trigger recipe validation or
execution flows intended for local or authenticated callers. In deployments
with powerful recipes, tool-enabled recipes, or admin endpoints, this can cause
unauthorized workflow execution, model/API spend, state changes, or recipe
registry reload operations.

This report does not claim arbitrary code execution by default.

## Suggested fix

Prefer one canonical Recipe server CLI path and enforce the same preflight for
every wrapper.

Recommended changes:

1. Remove or hard-disable the deprecated Typer `praisonai recipe serve` command,
   or make it delegate to the hardened `RecipeHandler.cmd_serve()` code path.
2. Add the same non-localhost/no-auth guard to `cli/commands/recipe.py`.
3. Treat `PRAISONAI_API_KEY` as a secret only when `auth=api-key` is selected;
   do not rely on the env var's presence alone unless the command also enables
   auth explicitly.
4. Fix the deprecated command's help examples so remote binding always includes
   auth.
5. Consider changing `--cors` default from `*` to no CORS or localhost origins.
6. Add regression tests that invoke the installed `praisonai.__main__.main()`
   entrypoint, not only the legacy feature handler:
   - `praisonai recipe serve --host 0.0.0.0` fails before launch unless auth is
     selected and configured;
   - `praisonai recipe serve --host 0.0.0.0 --admin` cannot expose
     `/admin/reload` without auth;
   - selected but misconfigured auth still returns `503`;
   - configured auth with no header returns `401`.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-5qw8-f2g9-ff29
- https://github.com/MervinPraison/PraisonAI
