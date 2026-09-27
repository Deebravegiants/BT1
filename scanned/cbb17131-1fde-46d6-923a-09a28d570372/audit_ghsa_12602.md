# [C] jFinal Server-Side Template Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-cgmm-c2m9-ff7r
CVE: CVE-2021-31635
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-26
Source: https://github.com/advisories/GHSA-cgmm-c2m9-ff7r
Type: github-advisory

## Affected
- Maven: `com.jfinal:jfinal` — affected >=0

## Details
Server-Side Template Injection (SSTI) vulnerability in jFinal v.4.9.08 allows a remote attacker to execute arbitrary code via the template function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31635
- https://github.com/jfinal/jfinal/issues/187
- https://gitee.com/jfinal/jfinal/issues/I3IXLE
