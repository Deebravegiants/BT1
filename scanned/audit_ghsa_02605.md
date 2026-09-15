# [H] Authentication bypass in Apache Zeppelin

## Summary
Severity: High
Advisory: GHSA-87p2-cvhq-q4mv
CVE: CVE-2020-13929
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-87p2-cvhq-q4mv
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin` — affected >=0 <0.10.0

## Details
Authentication bypass vulnerability in Apache Zeppelin allows an attacker to bypass Zeppelin authentication mechanism to act as another user. This issue affects Apache Zeppelin Apache Zeppelin version 0.9.0 and prior versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13929
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread.html/r768800925d6407a6a87ccae0ec98776b7bda50c0e3ed3d0130dad028%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r768800925d6407a6a87ccae0ec98776b7bda50c0e3ed3d0130dad028%40%3Cusers.zeppelin.apache.org%3E
- https://lists.apache.org/thread.html/r768800925d6407a6a87ccae0ec98776b7bda50c0e3ed3d0130dad028@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r768800925d6407a6a87ccae0ec98776b7bda50c0e3ed3d0130dad028@%3Cusers.zeppelin.apache.org%3E
- https://lists.apache.org/thread.html/r99529e175a7c1c9a26bd41a02802c8af7aa97319fe561874627eb999%40%3Cusers.zeppelin.apache.org%3E
- https://lists.apache.org/thread.html/r99529e175a7c1c9a26bd41a02802c8af7aa97319fe561874627eb999@%3Cusers.zeppelin.apache.org%3E
- https://security.gentoo.org/glsa/202311-04
- http://www.openwall.com/lists/oss-security/2021/09/02/2
