# [H] Nacos Spring vulnerable to Unsafe Deserialization

## Summary
Severity: High
Advisory: GHSA-v6c8-pwhq-288m
CVE: CVE-2023-39106
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-21
Source: https://github.com/advisories/GHSA-v6c8-pwhq-288m
Type: github-advisory

## Affected
- Maven: `com.alibaba.nacos:nacos-spring-context` — affected >=0

## Details
An issue in Nacos Group Nacos Spring Project v.1.1.1 and before allows a remote attacker to execute arbitrary code via the SnakeYamls Constructor() component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39106
- https://github.com/nacos-group/nacos-spring-project/issues/314
- https://github.com/nacos-group/nacos-spring-project
