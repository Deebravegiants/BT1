# [M]  PowerJob has a server-side request forgery vulnerability in PingPongUtils.java

## Summary
Severity: Medium
Advisory: GHSA-8xqm-6fj2-hfgf
CVE: CVE-2025-14518
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-12-11
Source: https://github.com/advisories/GHSA-8xqm-6fj2-hfgf
Type: github-advisory

## Affected
- Maven: `tech.powerjob:powerjob-common` — affected >=0

## Details
A vulnerability was identified in PowerJob up to 5.1.2. This vulnerability affects the function checkConnectivity of the file src/main/java/tech/powerjob/common/utils/net/PingPongUtils.java of the component Network Request Handler. The manipulation of the argument targetIp/targetPort leads to server-side request forgery. Remote exploitation of the attack is possible. The exploit is publicly available and might be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14518
- https://github.com/PowerJob/PowerJob/issues/1144
- https://github.com/PowerJob/PowerJob/issues/1144#issue-3673393002
- https://github.com/PowerJob/PowerJob
- https://vuldb.com/?ctiid.335856
- https://vuldb.com/?id.335856
- https://vuldb.com/?submit.702896
