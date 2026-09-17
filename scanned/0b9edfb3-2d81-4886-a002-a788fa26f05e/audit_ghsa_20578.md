# [C] Code injection in ShenYu

## Summary
Severity: Critical
Advisory: GHSA-gh38-x2wm-xmc8
CVE: CVE-2021-45029
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-gh38-x2wm-xmc8
Type: github-advisory

## Affected
- Maven: `org.apache.shenyu:shenyu-common` — affected >=2.4.0 <2.4.2

## Details
Groovy Code Injection & SpEL Injection which lead to Remote Code Execution. This issue affected Apache ShenYu 2.4.0 and 2.4.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45029
- https://github.com/apache/incubator-shenyu
- https://lists.apache.org/thread/3zzmwvg3012tg306x8o893fvdcssx639
- http://www.openwall.com/lists/oss-security/2022/01/25/8
- http://www.openwall.com/lists/oss-security/2022/01/26/1
