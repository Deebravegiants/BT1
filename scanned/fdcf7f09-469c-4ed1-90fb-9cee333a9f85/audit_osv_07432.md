# [C] BIT-resourcespace-2021-41950

## Summary
Severity: Critical
Advisory: BIT-resourcespace-2021-41950
Aliases: CVE-2021-41950
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-resourcespace-2021-41950
Type: osv

## Affected
- Bitnami: `resourcespace` — affected >=9.6.0

## Details
A directory traversal issue in ResourceSpace 9.6 before 9.6 rev 18277 allows remote unauthenticated attackers to delete arbitrary files on the ResourceSpace server via the provider and variant parameters in pages/ajax/tiles.php. Attackers can delete configuration or source code files, causing the application to become unavailable to all users.

## References
- http://svn.resourcespace.com/svn/rs/releases/9.6/pages/ajax/tiles.php
- https://www.horizon3.ai/multiple-vulnerabilities-in-resourcespace/
