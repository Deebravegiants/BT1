# [M] Open WebUI: Authenticated users can target arbitrary configured Ollama backends via unguarded url_idx path parameter

## Summary
Severity: Medium
Advisory: GHSA-9rpj-v7hf-vv2w
CVE: CVE-2026-54021
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-9rpj-v7hf-vv2w
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
## Summary

Several direct, index-addressed Ollama proxy routes accept a caller-supplied `url_idx`
path parameter and use it as a raw index into the admin-configured `OLLAMA_BASE_URLS`
list. Access control on these routes validates only whether the user may use the
requested *model*, never which *backend* the request is routed to. Any authenticated
user can append an arbitrary `url_idx` to force their request onto an Ollama backend
they were never authorized to reach, including internal, higher-privilege, or
explicitly admin-disabled backends.

## Affected endpoints

All indexed Ollama routes that resolve the backend through `get_ollama_url()`:

```
POST /ollama/api/chat/{url_idx}
POST /ollama/api/generate/{url_idx}
POST /ollama/api/embed/{url_idx}
POST /ollama/api/embeddings/{url_idx}
POST /ollama/v1/chat/completions/{url_idx}
POST /ollama/v1/completions/{url_idx}
POST /ollama/v1/messages/{url_idx}
POST /ollama/v1/responses/{url_idx}
```

## Root cause

`backend/open_webui/routers/ollama.py` — `get_ollama_url()` consults the
model-to-backend allow-list (`OLLAMA_MODELS[model]["urls"]`) only when `url_idx` is
omitted. When the caller supplies `url_idx`, that mapping is skipped and the value is
used directly as an index:

```python
async def get_ollama_url(request: Request, model: str, url_idx: Optional[int] = None):
    if url_idx is None:
        models = request.app.state.OLLAMA_MODELS
        if model not in models:
            raise HTTPException(...)
        url_idx = random.choice(models[model].get("urls", []))
    url = request.app.state.config.OLLAMA_BASE_URLS[url_idx]   # caller-controlled, no authz
    return url, url_idx
```

The outbound request is then sent to that backend using the backend's own configured
API key. Backends an admin has disabled (`OLLAMA_API_CONFIGS["<idx>"].enable = false`)
are hidden from model discovery but remain reachable through the indexed route, because
the disabled state is never re-checked at request time.

## Impact

A verified, non-admin user with read access to any single model can:
- route requests to internal / higher-capability / restricted Ollama backends in
  multi-backend deployments, bypassing backend-level isolation;
- reach backends the admin has explicitly disabled;
- have those requests authenticated with the target backend's configured API key
  (the key is used server-side; it is not returned to the attacker);
- consume the restricted backend's compute.

There is no cross-user data disclosure and no exfiltration of the backend credential
itself; the impact is unauthorized access to, and use of, restricted backend resources.

## Affected / Patched

- Affected: `<= 0.9.5`
- Patched: `>= 0.9.6`

## Fix

0.9.6 adds `validate_ollama_backend_idx()`, invoked on every indexed route (directly and
via `get_ollama_url()`), which returns 403 for any non-admin caller-supplied `url_idx`
that is not in the requested model's allowed `urls`. Because disabled backends are absent
from every model's `urls`, the same check also blocks routing to disabled backends.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-9rpj-v7hf-vv2w
- https://nvd.nist.gov/vuln/detail/CVE-2026-54021
- https://github.com/advisories/GHSA-9rpj-v7hf-vv2w
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2718.yaml
- https://pypi.org/project/open-webui
