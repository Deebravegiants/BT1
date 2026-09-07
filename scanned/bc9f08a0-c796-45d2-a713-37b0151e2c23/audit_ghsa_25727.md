# [M] Improper Input Validation and Allocation of Resources Without Limits or Throttling in poi-scratchpad

## Summary
Severity: Medium
Advisory: GHSA-mqvp-7rrg-9jxc
CVE: CVE-2022-26336
CWE: CWE-20, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-05
Source: https://github.com/advisories/GHSA-mqvp-7rrg-9jxc
Type: github-advisory

## Affected
- Maven: `org.apache.poi:poi-scratchpad` — affected >=3.8-beta1 <5.2.1

## Details
A shortcoming in the HMEF package of poi-scratchpad (Apache POI) allows an attacker to cause an Out of Memory exception. This package is used to read TNEF files (Microsoft Outlook and Microsoft Exchange Server). If an application uses poi-scratchpad to parse TNEF files and the application allows untrusted users to supply them, then a carefully crafted file can cause an Out of Memory exception. This issue affects poi-scratchpad version 5.2.0 and prior versions. Users are recommended to upgrade to poi-scratchpad 5.2.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26336
- https://lists.apache.org/thread/sprg0kq986pc2271dc3v2oxb1f9qx09j
- https://security.netapp.com/advisory/ntap-20221028-0006
