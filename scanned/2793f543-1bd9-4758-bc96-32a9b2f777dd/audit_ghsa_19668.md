# [C] OpenDaylight SFC Allows Unauthorized Privileged Execution via Crafted Request

## Summary
Severity: Critical
Advisory: GHSA-x65v-g96x-c6gw
CVE: CVE-2025-29315
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-24
Source: https://github.com/advisories/GHSA-x65v-g96x-c6gw
Type: github-advisory

## Affected
- Maven: `org.opendaylight.sfc:sfc-parent` — affected >=0

## Details
An issue in the Shiro-based RBAC (Role-based Access Control) mechanism of OpenDaylight Service Function Chaining (SFC) Subproject SFC Sodium-SR4 and below allows attackers to execute privileged operations via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-29315
- https://blog.csdn.net/weixin_43959580/article/details/144794289
- https://github.com/opendaylight/sfc
