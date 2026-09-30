# [H] WeGIA has SQL Injection in deletar_tag.php

## Summary
Severity: High
Advisory: CVE-2026-33991
Aliases: GHSA-74xm-6wgf-x37j
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33991
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Prior to version 3.6.7, the file `html/socio/sistema/deletar_tag.php` uses `extract($_REQUEST)` on line 14 and directly concatenates the `$id_tag` variable into SQL queries on lines 16-17 without prepared statements or sanitization. Version 3.6.7 patches the vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33991.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-74xm-6wgf-x37j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33991
