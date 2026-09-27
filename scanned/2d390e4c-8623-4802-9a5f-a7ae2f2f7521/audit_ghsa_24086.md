# [H] Deserialization of Untrusted Data in Gson

## Summary
Severity: High
Advisory: GHSA-4jrv-ppp4-jm57
CVE: CVE-2022-25647
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-4jrv-ppp4-jm57
Type: github-advisory

## Affected
- Maven: `com.google.code.gson:gson` — affected >=0 <2.8.9

## Details
The package `com.google.code.gson:gson` before 2.8.9 is vulnerable to Deserialization of Untrusted Data via the `writeReplace()` method in internal classes, which may lead to denial of service attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25647
- https://github.com/google/gson/pull/1991
- https://github.com/google/gson/pull/1991/commits
- https://github.com/google/gson
- https://lists.debian.org/debian-lts-announce/2022/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00009.html
- https://security.netapp.com/advisory/ntap-20220901-0009
- https://snyk.io/vuln/SNYK-JAVA-COMGOOGLECODEGSON-1730327
- https://www.debian.org/security/2022/dsa-5227
- https://www.oracle.com/security-alerts/cpujul2022.html
