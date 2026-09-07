# [H] Dolibarr Allows Code Injection through its Website Module

## Summary
Severity: High
Advisory: GHSA-676v-wh57-p375
CVE: CVE-2026-31018
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-676v-wh57-p375
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0

## Details
In Dolibarr ERP & CRM <= 22.0.4, PHP code detection and editing permission enforcement in the Website module is not applied consistently to all input parameters, allowing an authenticated user restricted to HTML/JavaScript editing to inject PHP code through unprotected inputs during website page creation.

A patch is available at https://github.com/Dolibarr/dolibarr/releases/tag/23.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31018
- https://github.com/Dolibarr/dolibarr/commit/ba28d16da4cc0c221f49a878fecc8425501ceb96
- https://github.com/Dolibarr/dolibarr
- https://github.com/Dolibarr/dolibarr/releases/tag/23.0.0
- https://github.com/PhDg1410/CVE/blob/main/CVE-2026-31018/README.md
- http://dolibarr.com
