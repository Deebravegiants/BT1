# [M] CVE-2023-49594

## Summary
Severity: Medium
Advisory: CVE-2023-49594
CVSS: 4.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-12-23
Source: https://osv.dev/vulnerability/CVE-2023-49594
Type: osv

## Details
An information disclosure vulnerability exists in the challenge functionality of instipod DuoUniversalKeycloakAuthenticator 1.0.7 plugin. A specially crafted HTTP request can lead to a disclosure of sensitive information. A user logging into Keycloak using  DuoUniversalKeycloakAuthenticator plugin triggers this vulnerability.

## References
- https://github.com/instipod/DuoUniversalKeycloakAuthenticator/releases/tag/1.0.8
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1907
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1907
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49594.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49594
