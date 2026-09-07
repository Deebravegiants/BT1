# [M] Goobi viewer Core has Cross-Site Scripting Vulnerability in User Nicknames

## Summary
Severity: Medium
Advisory: GHSA-2r9r-8fcg-m38g
CVE: CVE-2023-29016
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-07
Source: https://github.com/advisories/GHSA-2r9r-8fcg-m38g
Type: github-advisory

## Affected
- Maven: `io.goobi.viewer:viewer-core` — affected >=0 <23.03

## Details
### Impact
A cross-site scripting vulnerability has been identified in Goobi viewer core when using nicknames. An attacker could create a user account and enter malicious scripts into their profile's nickname, resulting in the execution in the user's browser when displaying the nickname on certain pages.

### Patches
The vulnerability has been fixed in version 23.03

If you have any questions or comments about this advisory:
* Email us at [support@intranda.com](mailto:support@intranda.com)

## References
- https://github.com/intranda/goobi-viewer-core/security/advisories/GHSA-2r9r-8fcg-m38g
- https://nvd.nist.gov/vuln/detail/CVE-2023-29016
- https://github.com/intranda/goobi-viewer-core/commit/8eadb32b3fdcb775678b74d95bc3df018a5d5238
- https://github.com/intranda/goobi-viewer-core
