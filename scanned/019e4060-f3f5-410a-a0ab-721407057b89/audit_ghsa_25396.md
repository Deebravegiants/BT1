# [M] Improper Certificate Validation in OkHttp

## Summary
Severity: Medium
Advisory: GHSA-4hc2-jh7r-wrc3
CVE: CVE-2016-2402
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4hc2-jh7r-wrc3
Type: github-advisory

## Affected
- Maven: `com.squareup.okhttp3:okhttp` — affected >=0 <2.7.4
- Maven: `com.squareup.okhttp3:okhttp` — affected >=3.0.0 <3.1.2

## Details
OkHttp before 2.7.4 and 3.x before 3.1.2 allows man-in-the-middle attackers to bypass certificate pinning by sending a certificate chain with a certificate from a non-pinned trusted CA and the pinned certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2402
- https://github.com/square/okhttp
- https://koz.io/pinning-cve-2016-2402
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26@%3Ccommits.pulsar.apache.org%3E
- https://publicobject.com/2016/02/11/okhttp-certificate-pinning-vulnerability
- http://www.openwall.com/lists/oss-security/2016/02/10/8
- http://www.openwall.com/lists/oss-security/2016/02/18/7
