# [C] Apache Tapestry allows deserialization of untrusted data

## Summary
Severity: Critical
Advisory: GHSA-vc39-x7w6-6vj7
CVE: CVE-2022-46366
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-02
Source: https://github.com/advisories/GHSA-vc39-x7w6-6vj7
Type: github-advisory

## Affected
- Maven: `org.apache.tapestry:tapestry-core` — affected >=3.0 <5.0.1

## Details
** UNSUPPORTED WHEN ASSIGNED ** Apache Tapestry 3.x allows deserialization of untrusted data, leading to remote code execution. This issue is similar to but distinct from CVE-2020-17531, which applies the the (also unsupported) 4.x version line. 

NOTE: This vulnerability only affects Apache Tapestry version line 3.x, which is no longer supported by the maintainer. Users are recommended to upgrade to a supported version line of Apache Tapestry.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46366
- https://github.com/mandiant/Vulnerability-Disclosures/blob/master/2022/MNDT-2022-0041/MNDT-2022-0041.md
- https://lists.apache.org/thread/bwn1vjrvz1hq0wbdzj23wz322244swhj
- http://www.openwall.com/lists/oss-security/2022/12/02/1
