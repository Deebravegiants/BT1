# [H] Apache Ranger code execution vulnerability in policy expressions

## Summary
Severity: High
Advisory: GHSA-89gw-cffj-mqg9
CVE: CVE-2022-45048
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-89gw-cffj-mqg9
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=2.3.0 <2.4.0

## Details
Authenticated users with appropriate privileges can create policies having expressions that can exploit code execution vulnerability. This issue affects Apache Ranger: 2.3.0. Users are recommended to update to version 2.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45048
- https://github.com/apache/ranger
- https://lists.apache.org/thread/6rpzwy1smdhr60tsh1ydknn3kdm45bb6
