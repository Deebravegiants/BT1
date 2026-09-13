# [H] Open WebUI's Base Model Routing Bypasses Access Control via Model Chaining

## Summary
Severity: High
Advisory: GHSA-9vvh-qmjx-p4q8
CVE: CVE-2026-44555
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-9vvh-qmjx-p4q8
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
# Base Model Routing Bypasses Access Control via Model Chaining

## Affected Component

Model chaining via `base_model_id`:
- `backend/open_webui/routers/models.py` (lines 170-214, `create_new_model`)
- `backend/open_webui/routers/models.py` (lines 254-308, `import_models`)
- `backend/open_webui/main.py` (lines 1696-1711, base model resolution in chat completion)
- `backend/open_webui/routers/openai.py` (lines 1032-1037, base model payload rewrite)
- `backend/open_webui/routers/ollama.py` (lines 1086-1090, base model payload rewrite)
- `backend/open_webui/utils/models.py` (line 380, `check_model_access` — checks user-facing model only)

## Affected Versions

Current main branch (commit `6fdd19bf1`) and likely all versions with the model chaining (`base_model_id`) feature.

## Description

Open WebUI supports model composition via `base_model_id`: a user-defined model (e.g., "Cheap Assistant") can reference an existing base model (e.g., "gpt-4-turbo-restricted") that provides the actual inference capability. When a user queries the composed model, the access control pipeline verifies the user has access to the composed model but never re-verifies access to the chained base model.

Additionally, the model creation and import endpoints accept arbitrary `base_model_id` values without checking that the caller has access to that base model. Combined, this allows any user with the default model creation permission to create a model that chains to a restricted base model — and then invoke it, causing the server to dispatch the request to the restricted base model using the admin-configured API key.

```python
# utils/models.py:380 — access check runs against the user-facing model only
def check_model_access(user, model):
    if user.role == 'user':
        ...check access grants on `model`...

# main.py:1696-1711 — base model resolved without access check
base_model = request.app.state.MODELS.get(model.info.base_model_id)
if base_model:
    # payload["model"] is rewritten to base_model.id
    # but no check_model_access(user, base_model) is performed

# openai.py:1032-1037 / ollama.py:1086-1090 — the rewritten payload is dispatched
payload['model'] = base_model_id
```

## Attack Scenario

1. Admin provisions a premium/restricted model `gpt-4-turbo-restricted` and configures access grants so only the "ML Engineers" group can use it.
2. Attacker (a regular user not in that group) calls:
   ```
   POST /api/v1/models/create
   {
     "id": "cheap-assistant",
     "name": "Cheap Assistant",
     "base_model_id": "gpt-4-turbo-restricted",
     "params": {},
     "meta": {}
   }
   ```
   The creation endpoint does not validate the attacker's access to `gpt-4-turbo-restricted`.
3. Attacker now owns `cheap-assistant`. `check_model_access(attacker, cheap-assistant)` passes trivially because they are the owner.
4. Attacker sends:
   ```
   POST /api/chat/completions
   {"model": "cheap-assistant", "messages": [...]}
   ```
5. At `main.py:1696`, the pipeline resolves `cheap-assistant.base_model_id` to `gpt-4-turbo-restricted`, rewrites `payload["model"]` to the base model ID, and dispatches the upstream request with the admin-configured API key for the backend.
6. The attacker receives responses from the restricted model, bypassing the access grant policy.

The same bypass is available via the import endpoint, which additionally allows overwriting existing models (see related finding on model import ownership).

## Impact

- Regular users can query restricted models by chaining through a self-owned wrapper model
- Access control on `gpt-4-turbo-restricted` (or equivalent paid/tiered/internal models) becomes silently ineffective
- Direct cost impact on pay-per-token backends (OpenAI, Anthropic, Azure) — the admin's API key is used for requests the admin intended to forbid
- Creates a false sense of security — the admin sees access restrictions work through the standard model selector but not through user-created chains

## Preconditions

- Attacker must have model creation permission (default `workspace.models` permission, granted to all users by default)
- A restricted base model must exist on the instance (the target of the chain)

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-9vvh-qmjx-p4q8
- https://nvd.nist.gov/vuln/detail/CVE-2026-44555
- https://github.com/open-webui/open-webui
