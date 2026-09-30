# [C] Code injection in PowerJob

## Summary
Severity: Critical
Advisory: GHSA-2h26-qfxm-r3pq
CVE: CVE-2023-37754
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-2h26-qfxm-r3pq
Type: github-advisory

## Affected
- Maven: `tech.powerjob:powerjob-common` — affected >=0

## Details
PowerJob v4.3.3 was discovered to contain a remote command execution (RCE) vulnerability via the instanceId parameter at /instance/detail.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37754
- https://github.com/PowerJob/PowerJob/issues/675
- https://github.com/PowerJob/PowerJob
- https://novysodope.github.io/2023/07/02/100
