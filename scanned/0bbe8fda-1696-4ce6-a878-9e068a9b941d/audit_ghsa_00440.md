# [H] Bouncy Castle has a flaw in the Low-level interface to RSA key pair generator

## Summary
Severity: High
Advisory: GHSA-xqj7-j8j5-f2xr
CVE: CVE-2018-1000180
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-xqj7-j8j5-f2xr
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=0 <1.60
- Maven: `org.bouncycastle:bcprov-jdk15` — affected >=0 <1.60
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0 <1.60

## Details
Bouncy Castle BC 1.54 - 1.59, BC-FJA 1.0.0, BC-FJA 1.0.1 and earlier have a flaw in the Low-level interface to RSA key pair generator, specifically RSA Key Pairs generated in low-level API with added certainty may have less M-R tests than expected. This appears to be fixed in versions BC 1.60 beta 4 and later, BC-FJA 1.0.2 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000180
- https://github.com/bcgit/bc-java/commit/22467b6e8fe19717ecdf201c0cf91bacf04a55ad
- https://github.com/bcgit/bc-java/commit/73780ac522b7795fc165630aba8d5f5729acc839
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.debian.org/security/2018/dsa-4233
- https://www.bountysource.com/issues/58293083-rsa-key-generation-computation-of-iterations-for-mr-primality-test
- https://security.netapp.com/advisory/ntap-20190204-0003
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451@%3Csolr-user.lucene.apache.org%3E
- https://github.com/bcgit/bc-java/wiki/CVE-2018-1000180
- https://github.com/advisories/GHSA-xqj7-j8j5-f2xr
- https://access.redhat.com/errata/RHSA-2019:0877
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2018:2643
- https://access.redhat.com/errata/RHSA-2018:2428
- https://access.redhat.com/errata/RHSA-2018:2425
