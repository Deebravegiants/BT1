# [H] OpenSTAManager contains an arbitrary file upload vulnerability in its module update functionality 

## Summary
Severity: High
Advisory: GHSA-rm34-fg4m-39mw
CVE: CVE-2026-38751
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-rm34-fg4m-39mw
Type: github-advisory

## Affected
- Packagist: `devcode-it/openstamanager` — affected >=0

## Details
OpenSTAManager versions 2.10 and earlier contain an arbitrary file upload vulnerability in the module update functionality (modules/aggiornamenti/upload_modules.php).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38751
- https://github.com/devcode-it/openstamanager
- https://github.com/fuutianyii/poc
