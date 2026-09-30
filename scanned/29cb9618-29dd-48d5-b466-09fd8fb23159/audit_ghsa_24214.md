# [H] JFinal file validation vulnerability

## Summary
Severity: High
Advisory: GHSA-279p-pc38-xx4p
CVE: CVE-2019-17352
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-279p-pc38-xx4p
Type: github-advisory

## Affected
- Maven: `com.jfinal:jfinal` — affected >=0 <4.5

## Details
In JFinal cos before 2019-08-13, as used in JFinal 4.4, there is a vulnerability that can bypass the isSafeFile() function: one can upload any type of file. For example, a .jsp file may be stored and almost immediately deleted, but this deletion step does not occur for certain exceptions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17352
- https://github.com/jfinal/jfinal/issues/171
- https://gitee.com/jfinal/cos
- https://gitee.com/jfinal/cos/commit/5eb23d6e384abaad19faa7600d14c9a2f525946a
- https://gitee.com/jfinal/cos/commit/8d26eec61f0d072a68bf7393cf3a8544a1112130
