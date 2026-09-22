# [M] WeGIA < 3.9.2 Insecure Direct Object Reference via profile_funcionario.php

## Summary
Severity: Medium
Advisory: CVE-2026-76634
Aliases: GHSA-jqh5-66qr-85qv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-76634
Type: osv

## Details
WeGIA before 3.9.2 contains an insecure direct object reference vulnerability in the employee profile page that allows authenticated attackers to access arbitrary employee records by injecting an id_pessoa parameter through a request extraction function that overwrites the session-derived identifier. Attackers can enumerate all user identifiers to retrieve full profile data for any employee account, including name, CPF, address, contact details, and administrative flags.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76634.json
- https://github.com/LabRedesCefetRJ/WeGIA/releases#release-3.9.2
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-jqh5-66qr-85qv
- https://nvd.nist.gov/vuln/detail/CVE-2026-76634
- https://www.vulncheck.com/advisories/wegia-insecure-direct-object-reference-via-profile-funcionario-php
- https://github.com/LabRedesCefetRJ/WeGIA
