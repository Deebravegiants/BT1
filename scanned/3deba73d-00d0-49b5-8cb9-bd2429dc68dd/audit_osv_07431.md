# [C] BIT-resourcespace-2021-41765

## Summary
Severity: Critical
Advisory: BIT-resourcespace-2021-41765
Aliases: CVE-2021-41765
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-resourcespace-2021-41765
Type: osv

## Affected
- Bitnami: `resourcespace` — affected >=9.6.0

## Details
A SQL injection issue in pages/edit_fields/9_ajax/add_keyword.php of ResourceSpace 9.5 and 9.6 < rev 18274 allows remote unauthenticated attackers to execute arbitrary SQL commands via the k parameter. This allows attackers to uncover the full contents of the ResourceSpace database, including user session cookies. An attacker who gets an admin user session cookie can use the session cookie to execute arbitrary code on the server.

## References
- http://svn.resourcespace.com/svn/rs/releases/9.6/pages/edit_fields/9_ajax/add_keyword.php
- https://www.horizon3.ai/multiple-vulnerabilities-in-resourcespace/
