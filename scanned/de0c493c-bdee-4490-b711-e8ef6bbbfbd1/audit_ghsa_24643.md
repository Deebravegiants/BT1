# [M] Insufficient Data Verification in io.really:jwt-scala

## Summary
Severity: Medium
Advisory: GHSA-9pxm-8g95-q5xr
CVE: CVE-2017-10862
CWE: CWE-345
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9pxm-8g95-q5xr
Type: github-advisory

## Affected
- Maven: `io.really:jwt-scala` — affected >=0

## Details
jwt-scala 1.2.2 and earlier fails to verify token signatures correctly which may lead to an attacker being able to pass specially crafted JWT data as a correctly signed token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-10862
- https://github.com/reallylabs/jwt-scala
- https://jvn.jp/en/vu/JVNVU90916766/index.html
