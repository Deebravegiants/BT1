# [H] Out-of-Memory Error in Bouncy Castle Crypto

## Summary
Severity: High
Advisory: GHSA-2mh8-gx2m-mr75
CVE: CVE-2019-17359
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-10-17
Source: https://github.com/advisories/GHSA-2mh8-gx2m-mr75
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=1.63 <1.64

## Details
The ASN.1 parser in Bouncy Castle Crypto (aka BC Java) 1.63 can trigger a large attempted memory allocation, and resultant OutOfMemoryError error, via crafted ASN.1 data. This is fixed in 1.64.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17359
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.bouncycastle.org/releasenotes.html
- https://www.bouncycastle.org/latest_releases.html
- https://security.netapp.com/advisory/ntap-20191024-0006
- https://lists.apache.org/thread.html/re60f980c092ada4bfe236dcfef8b6ca3e8f3b150fc0f51b8cc13d59d@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r91b07985b1307390a58c5b9707f0b28ef8e9c9e1c86670459f20d601@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r8ecb5b76347f84b6e3c693f980dbbead88c25f77b815053c4e6f2c30@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r79b6a6aa0dd1aeb57bd253d94794bc96f1ec005953c4bd5414cc0db0@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r4d475dcaf4f57115fa57d8e06c3823ca398b35468429e7946ebaefdc@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r467ade3fef3493f1fff1a68a256d087874e1f858ad1de7a49fe05d27@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r16c3a90cb35ae8a9c74fd5c813c16d6ac255709c9f9d71cd409e007d@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r02f887807a49cfd1f1ad53f7a61f3f8e12f60ba2c930bec163031209@%3Ccommits.tomee.apache.org%3E
