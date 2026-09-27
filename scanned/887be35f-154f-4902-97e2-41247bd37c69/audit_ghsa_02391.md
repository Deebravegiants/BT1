# [M] Incorrect Access Control in Nacos

## Summary
Severity: Medium
Advisory: GHSA-qf76-pr7x-h7r4
CVE: CVE-2020-19676
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-qf76-pr7x-h7r4
Type: github-advisory

## Affected
- Maven: `com.alibaba.nacos:nacos-common` — affected >=0 <1.2.0

## Details
Nacos 1.1.4 is affected by: Incorrect Access Control. An environment can be set up locally to get the service details interface. Then other Nacos service names can be accessed through the service list interface. Service details can then be accessed when not logged in. (detail:https://github.com/alibaba/nacos/issues/2284)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-19676
- https://github.com/alibaba/nacos/issues/1105
- https://github.com/alibaba/nacos/issues/2284
- https://github.com/alibaba/nacos/releases/tag/1.2.0
