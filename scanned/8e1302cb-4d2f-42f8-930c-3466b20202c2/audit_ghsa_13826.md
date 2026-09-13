# [C] H2O local file inclusion vulnerability

## Summary
Severity: Critical
Advisory: GHSA-6mv8-95x5-xcq9
CVE: CVE-2023-6038
CWE: CWE-29, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-6mv8-95x5-xcq9
Type: github-advisory

## Affected
- Maven: `ai.h2o:h2o-core` — affected >=0

## Details
A Local File Inclusion (LFI) vulnerability exists in the h2o-3 REST API, allowing unauthenticated remote attackers to read arbitrary files on the server with the permissions of the user running the h2o-3 instance. This issue affects the default installation and does not require user interaction. The vulnerability can be exploited by making specific GET or POST requests to the ImportFiles and ParseSetup endpoints, respectively. This issue was identified in version 3.40.0.4 of h2o-3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6038
- https://github.com/h2oai/h2o-3
- https://huntr.com/bounties/380fce33-fec5-49d9-a101-12c972125d8c
