# [C] Apache Dubbo: Bypass deny serialize list check in Apache Dubbo

## Summary
Severity: Critical
Advisory: GHSA-97rv-88gf-phvr
CVE: CVE-2023-46279
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-15
Source: https://github.com/advisories/GHSA-97rv-88gf-phvr
Type: github-advisory

## Affected
- Maven: `org.apache.dubbo:dubbo` — affected >=3.1.5 <3.1.6

## Details
Deserialization of Untrusted Data vulnerability in Apache Dubbo.This issue only affects Apache Dubbo 3.1.5.

Users are recommended to upgrade to the latest version, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46279
- https://github.com/apache/dubbo
- https://lists.apache.org/thread/zw53nxrkrfswmk9n3sfwxmcj7x030nmo
- http://www.openwall.com/lists/oss-security/2023/12/15/3
