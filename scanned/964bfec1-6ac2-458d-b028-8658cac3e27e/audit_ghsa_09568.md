# [H] Apache OpenMeetings Uses Hard-coded Cryptographic Key

## Summary
Severity: High
Advisory: GHSA-wqxq-w68r-wg85
CVE: CVE-2026-33266
CWE: CWE-321
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-wqxq-w68r-wg85
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=6.1.0 <9.0.0

## Details
Use of Hard-coded Cryptographic Key vulnerability in Apache OpenMeetings.

The remember-me cookie encryption key is set to default value in openmeetings.properties and not being auto-rotated. In case OM admin hasn't changed the default encryption key, an attacker who has stolen a cookie from a logged-in user can get full user credentials.


This issue affects Apache OpenMeetings: from 6.1.0 before 9.0.0.

Users are recommended to upgrade to version 9.0.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33266
- https://github.com/apache/openmeetings
- https://lists.apache.org/thread/b05jnp9563v49zq494lox9kjbhhf2w66
- http://www.openwall.com/lists/oss-security/2026/04/09/11
