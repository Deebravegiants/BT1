# [H] XXL-CONF Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-8j39-fgfp-vxh8
CVE: CVE-2018-20094
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-12-19
Source: https://github.com/advisories/GHSA-8j39-fgfp-vxh8
Type: github-advisory

## Affected
- Maven: `com.xuxueli:xxl-conf-admin` — affected >=0

## Details
An issue was discovered in XXL-CONF 1.6.0. There is a path traversal vulnerability via `../` in the keys parameter that can download any configuration file, related to `ConfController.java` and `PropUtil.java`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20094
- https://github.com/xuxueli/xxl-conf/issues/61
- https://github.com/xuxueli/xxl-conf
- https://github.com/xuxueli/xxl-conf/blob/6726dfe7979ea6d8fb983771471cde69789de632/xxl-conf-admin/src/main/java/com/xxl/conf/admin/controller/ConfController.java
