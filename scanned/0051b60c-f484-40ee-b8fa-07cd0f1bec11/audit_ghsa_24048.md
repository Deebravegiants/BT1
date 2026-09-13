# [M] Observable Discrepancy in BouncyCastle

## Summary
Severity: Medium
Advisory: GHSA-wrwf-pmmj-w989
CVE: CVE-2017-13098
CWE: CWE-203
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wrwf-pmmj-w989
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0 <1.0.3

## Details
BouncyCastle TLS prior to version 1.0.3, when configured to use the JCE (Java Cryptography Extension) for cryptographic functions, provides a weak Bleichenbacher oracle when any TLS cipher suite using RSA key exchange is negotiated. An attacker can recover the private key from a vulnerable application. This vulnerability is referred to as "ROBOT."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-13098
- https://github.com/bcgit/bc-java/commit/a00b684465b38d722ca9a3543b8af8568e6bad5c
- https://github.com/bcgit/bc-java
- https://robotattack.org
- https://security.netapp.com/advisory/ntap-20171222-0001
- https://www.debian.org/security/2017/dsa-4072
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00011.html
- http://www.kb.cert.org/vuls/id/144389
