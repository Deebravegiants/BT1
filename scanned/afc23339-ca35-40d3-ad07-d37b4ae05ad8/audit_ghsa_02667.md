# [M] Cross-site Scripting in Apache Zeppelin

## Summary
Severity: Medium
Advisory: GHSA-mf7q-gw5f-q8jj
CVE: CVE-2021-27578
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-mf7q-gw5f-q8jj
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin` — affected >=0 <0.9.0

## Details
Cross Site Scripting vulnerability in markdown interpreter of Apache Zeppelin allows an attacker to inject malicious scripts. This issue affects Apache Zeppelin Apache Zeppelin versions prior to 0.9.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27578
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread.html/r31012f2c8e39a5e12e14c1de030012cb8b51c037d953d73b291b7b50%40%3Cusers.zeppelin.apache.org%3E
- https://lists.apache.org/thread.html/r31012f2c8e39a5e12e14c1de030012cb8b51c037d953d73b291b7b50@%3Cusers.zeppelin.apache.org%3E
- https://lists.apache.org/thread.html/r90590aa5ea788128ecc2e822e1e64d5200b4cb92b06707b38da4cb3d%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r90590aa5ea788128ecc2e822e1e64d5200b4cb92b06707b38da4cb3d%40%3Cusers.zeppelin.apache.org%3E
- https://lists.apache.org/thread.html/r90590aa5ea788128ecc2e822e1e64d5200b4cb92b06707b38da4cb3d@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r90590aa5ea788128ecc2e822e1e64d5200b4cb92b06707b38da4cb3d@%3Cusers.zeppelin.apache.org%3E
- https://security.gentoo.org/glsa/202311-04
- http://www.openwall.com/lists/oss-security/2021/09/02/3
