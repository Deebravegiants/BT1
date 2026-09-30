# [C] CodenameOne Pending Intent vulnerability

## Summary
Severity: Critical
Advisory: GHSA-p6xq-9h8r-v544
CVE: CVE-2022-4903
CWE: CWE-668, CWE-927
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-10
Source: https://github.com/advisories/GHSA-p6xq-9h8r-v544
Type: github-advisory

## Affected
- Maven: `com.codenameone:codenameone-core` — affected >=0 <7.0.71

## Details
A vulnerability was found in CodenameOne 7.0.70. The manipulation leads to use of implicit intent for sensitive communication. It is possible to launch the attack remotely. Upgrading to version 7.0.71 is able to address this issue. The name of the patch is dad49c9ef26a598619fc48d2697151a02987d478. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4903
- https://github.com/codenameone/CodenameOne/issues/3583
- https://github.com/codenameone/CodenameOne/commit/dad49c9ef26a598619fc48d2697151a02987d478
- https://github.com/codenameone/CodenameOne
- https://github.com/codenameone/CodenameOne/releases/tag/7.0.71
- https://vuldb.com/?ctiid.220470
- https://vuldb.com/?id.220470
