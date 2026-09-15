# [C] WeGIA lacks authentication verification in adicionar_tipo_docs_atendido.php

## Summary
Severity: Critical
Advisory: CVE-2026-28408
Aliases: GHSA-xq3w-xwxj-fg2q
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28408
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Prior to version 3.6.5, the script in adicionar_tipo_docs_atendido.php does not go through the project's central controller and does not have its own authentication and permission checks. A malicious user could make a request through tools like Postman or the file's URL on the web to access features exclusive to employees. The vulnerability allows external parties to inject unauthorized data in massive quantities into the application server's storage. Version 3.6.5 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28408.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-xq3w-xwxj-fg2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-28408
