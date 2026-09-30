# [M] Command Injection in Apache James

## Summary
Severity: Medium
Advisory: GHSA-84wg-rgp8-2hg4
CVE: CVE-2021-38542
CWE: CWE-327, CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-84wg-rgp8-2hg4
Type: github-advisory

## Affected
- Maven: `org.apache.james:james-server` — affected >=0 <3.6.1

## Details
Apache James prior to release 3.6.1 is vulnerable to a buffering attack relying on the use of the STARTTLS command. This can result in Man-in -the-middle command injection attacks, leading potentially to leakage of sensible information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38542
- https://www.openwall.com/lists/oss-security/2022/01/04/1
- http://www.openwall.com/lists/oss-security/2022/01/04/1
- http://www.openwall.com/lists/oss-security/2022/09/20/1
