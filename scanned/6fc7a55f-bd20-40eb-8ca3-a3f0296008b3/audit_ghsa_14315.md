# [M] Goobi viewer Core Reflected Cross-Site Scripting Vulnerability Using LOGID Parameter

## Summary
Severity: Medium
Advisory: GHSA-7v7g-9vx6-vcg2
CVE: CVE-2023-29014
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-07
Source: https://github.com/advisories/GHSA-7v7g-9vx6-vcg2
Type: github-advisory

## Affected
- Maven: `io.goobi.viewer:viewer-core` — affected >=0 <23.03

## Details
### Impact
A reflected cross-site scripting vulnerability has been identified in Goobi viewer core when evaluating the LOGID parameter. An attacker could trick a user into following a specially crafted link to a Goobi viewer installation, resulting in the execution of malicious script code in the user's browser.

### Patches
The vulnerability has been fixed in version 23.03

### Credits
We would like to thank [RUS-CERT](https://cert.uni-stuttgart.de/) for reporting this issues.

If you have any questions or comments about this advisory:
* Email us at [support@intranda.com](mailto:support@intranda.com)

## References
- https://github.com/intranda/goobi-viewer-core/security/advisories/GHSA-7v7g-9vx6-vcg2
- https://nvd.nist.gov/vuln/detail/CVE-2023-29014
- https://github.com/intranda/goobi-viewer-core/commit/c29efe60e745a94d03debc17681c4950f3917455
- https://github.com/intranda/goobi-viewer-core
