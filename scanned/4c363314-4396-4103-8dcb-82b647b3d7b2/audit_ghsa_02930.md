# [C] Template injection in thymeleaf-spring5

## Summary
Severity: Critical
Advisory: GHSA-qcj6-jqrg-4wp2
CVE: CVE-2021-43466
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-qcj6-jqrg-4wp2
Type: github-advisory

## Affected
- Maven: `org.thymeleaf:thymeleaf-spring5` — affected >=0 <3.0.13.RELEASE

## Details
In the thymeleaf-spring5:3.0.12 component, thymeleaf combined with specific scenarios in template injection may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43466
- https://github.com/thymeleaf/thymeleaf-spring/issues/263#issuecomment-977199524
- https://gitee.com/wayne_wwang/wayne_wwang/blob/master/2021/10/31/ruoyi+thymeleaf-rce/index.html
- https://github.com/thymeleaf/thymeleaf-spring
- https://security.netapp.com/advisory/ntap-20221014-0001
- https://vuldb.com/?id.186365
