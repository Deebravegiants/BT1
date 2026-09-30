# [M] Local Deep Research's API keys are stored in plain text

## Summary
Severity: Medium
Advisory: CVE-2025-57806
Aliases: GHSA-4h8c-qrcq-cv5c
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-09-03
Source: https://osv.dev/vulnerability/CVE-2025-57806
Type: osv

## Details
Local Deep Research is an AI-powered research assistant for deep, iterative research. Versions 0.2.0 through 0.6.7 stored confidential information, including API keys, in a local SQLite database without encryption. This behavior was not clearly documented outside of the database architecture page. Users were not given the ability to configure the database location, allowing anyone with access to the container or host filesystem to retrieve sensitive data in plaintext by accessing the .db file. This is fixed in version 1.0.0.

## References
- http://github.com/LearningCircuit/local-deep-research/releases/tag/v1.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57806.json
- https://github.com/LearningCircuit/local-deep-research/security/advisories/GHSA-4h8c-qrcq-cv5c
- https://nvd.nist.gov/vuln/detail/CVE-2025-57806
- https://github.com/LearningCircuit/local-deep-research/pull/578
