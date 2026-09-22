# [C] Dataease before 1.11.2 allows arbitrary code execution via crafter plugin

## Summary
Severity: Critical
Advisory: GHSA-5469-c5p2-xv5g
CVE: CVE-2022-34113
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-23
Source: https://github.com/advisories/GHSA-5469-c5p2-xv5g
Type: github-advisory

## Affected
- Maven: `io.dataease:dataease-plugin-common` — affected >=0 <1.11.2

## Details
An issue in the component /api/plugin/upload of Dataease v1.11.1 allows attackers to execute arbitrary code via a crafted plugin. Version 1.11.2 contains a patch for the problem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34113
- https://github.com/dataease/dataease/issues/2431
- https://github.com/dataease/dataease
- https://github.com/dataease/dataease/releases/tag/v1.11.2
