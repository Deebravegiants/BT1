# [M] Junrar vulnerable to Infinite Loop

## Summary
Severity: Medium
Advisory: GHSA-5xqr-grq4-qwgx
CVE: CVE-2018-12418
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-5xqr-grq4-qwgx
Type: github-advisory

## Affected
- Maven: `com.github.junrar:junrar` — affected >=0 <1.0.1

## Details
Archive.java in Junrar before 1.0.1, as used in Apache Tika and other products, is affected by a denial of service vulnerability due to an infinite loop when handling corrupt RAR files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12418
- https://github.com/junrar/junrar/pull/8
- https://github.com/junrar/junrar/commit/ad8d0ba8e155630da8a1215cee3f253e0af45817
- https://github.com/advisories/GHSA-5xqr-grq4-qwgx
- https://github.com/junrar/junrar
