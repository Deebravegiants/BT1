# [C] Improper Authentication in Apache ShenYu Admin

## Summary
Severity: Critical
Advisory: GHSA-vpfp-5gwq-g533
CVE: CVE-2021-37580
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-17
Source: https://github.com/advisories/GHSA-vpfp-5gwq-g533
Type: github-advisory

## Affected
- Maven: `org.apache.shenyu:shenyu-admin` — affected >=2.3.0 <2.4.1

## Details
A flaw was found in Apache ShenYu Admin. The incorrect use of JWT in ShenyuAdminBootstrap allows an attacker to bypass authentication. This issue affected Apache ShenYu 2.3.0 and 2.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37580
- https://github.com/apache/shenyu/commit/f78adb26926ba53b4ec5c21f2cf7e931461d601d
- https://github.com/apache/shenyu
- https://github.com/apache/shenyu/releases/tag/v2.4.1
- https://lists.apache.org/thread/o15j25qwtpcw62k48xw1tnv48skh3zgb
- http://www.openwall.com/lists/oss-security/2021/11/16/1
