# [H] Password exposure in ShenYu

## Summary
Severity: High
Advisory: GHSA-7wq4-89xx-g62j
CVE: CVE-2022-23223
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-7wq4-89xx-g62j
Type: github-advisory

## Affected
- Maven: `org.apache.shenyu:shenyu-common` — affected >=2.4.0 <2.4.2

## Details
On Apache ShenYu versions 2.4.0 and 2.4.1, and endpoint existed that disclosed the passwords of all users. Users are recommended to upgrade to version 2.4.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23223
- https://github.com/apache/shenyu/pull/2357
- https://github.com/apache/shenyu/commit/0e826ceae97a1258cb15c73a3072118c920e8654
- https://github.com/apache/incubator-shenyu
- https://github.com/apache/incubator-shenyu/releases/tag/v2.4.2
- https://lists.apache.org/thread/q2gg6ny6lpkph7nkrvjzqdvqpm805v8s
- http://www.openwall.com/lists/oss-security/2022/01/25/7
- http://www.openwall.com/lists/oss-security/2022/01/26/4
