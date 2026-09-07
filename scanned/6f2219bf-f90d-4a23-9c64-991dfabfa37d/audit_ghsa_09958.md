# [H] SillyTavern: Path Traversal in `/api/chats/export` and `/api/chats/delete` allows arbitrary file read/delete within user data root

## Summary
Severity: High
Advisory: GHSA-vprr-q85p-79mf
CVE: CVE-2026-34524
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-vprr-q85p-79mf
Type: github-advisory

## Affected
- npm: `sillytavern` — affected >=0 <1.17.0

## Details
## Summary
A Path Traversal vulnerability in chat endpoints allows an authenticated attacker to read and delete arbitrary files under their user data root (for example `secrets.json` and `settings.json`) by supplying `avatar_url=".."`.

### Details
The input validator used by `avatar_url` blocks only `/` and NUL bytes, but does not block traversal segments like `..`.

Evidence:
- Weak validator regex (does not reject `..`):  
  <https://github.com/SillyTavern/SillyTavern/blob/b7bb8be35a5c779b4db12a4a5b94d7e49096071c/src/middleware/validateFileName.js#L24-L27>
- Vulnerable delete path construction:  
  <https://github.com/SillyTavern/SillyTavern/blob/b7bb8be35a5c779b4db12a4a5b94d7e49096071c/src/endpoints/chats.js#L575-L577>
- Vulnerable export path construction:  
  <https://github.com/SillyTavern/SillyTavern/blob/b7bb8be35a5c779b4db12a4a5b94d7e49096071c/src/endpoints/chats.js#L595-L598>
- Endpoint auth context (authenticated user access):  
  <https://github.com/SillyTavern/SillyTavern/blob/b7bb8be35a5c779b4db12a4a5b94d7e49096071c/src/server-main.js#L239>

Because `avatar_url=".."` is accepted, `path.join(<user>/chats, "..")` resolves to `<user>/`, enabling direct access to files outside the chats directory.

### PoC
Prerequisites:
- Valid authenticated session cookie (`cookie.txt`)
- Valid CSRF token (`$TOKEN`)

Read sensitive file (`secrets.json`):

```bash
curl -b cookie.txt -H "x-csrf-token: $TOKEN" -H "content-type: application/json" \
  -d '{"avatar_url":"..","is_group":false,"file":"secrets.json","format":"jsonl","exportfilename":"x"}' \
  http://TARGET:8000/api/chats/export
```

Delete sensitive file (`settings.json`):

```bash
curl -b cookie.txt -H "x-csrf-token: $TOKEN" -H "content-type: application/json" \
  -d '{"avatar_url":"..","chatfile":"settings.json"}' \
  http://TARGET:8000/api/chats/delete
```

### Impact
- Confidentiality: exposed per-user secrets and config data.
- Integrity/Availability: attacker can delete critical per-user files and break account operation.
- Risk is significant in multi-user or remotely reachable deployments.

### Resolution

The issue was addressed in version 1.17.0

## References
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-vprr-q85p-79mf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34524
- https://github.com/SillyTavern/SillyTavern
- https://github.com/SillyTavern/SillyTavern/releases/tag/1.17.0
