# [H] WeGIA has SQL Injection via Session Variable Override in DespachoControle.php

## Summary
Severity: High
Advisory: CVE-2026-40285
Aliases: GHSA-666r-v2m7-xgp9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40285
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Versions prior to 3.6.10 contain a SQL injection vulnerability in dao/memorando/UsuarioDAO.php. The cpf_usuario POST parameter overwrites the session-stored user identity via extract($_REQUEST) in DespachoControle::verificarDespacho(), and the attacker-controlled value is then interpolated directly into a raw SQL query, allowing any authenticated user to query the database under an arbitrary identity. Version 3.6.10 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40285.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-666r-v2m7-xgp9
- https://nvd.nist.gov/vuln/detail/CVE-2026-40285
