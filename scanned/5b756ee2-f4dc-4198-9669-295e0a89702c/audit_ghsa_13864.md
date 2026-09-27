# [H] Insecure Permissions issue in jeecg-boot

## Summary
Severity: High
Advisory: GHSA-rwhw-6c6r-2823
CVE: CVE-2021-37304
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-03
Source: https://github.com/advisories/GHSA-rwhw-6c6r-2823
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-base` — affected >=0

## Details
An Insecure Permissions issue in jeecg-boot 2.4.5 allows unauthenticated remote attackers to gain escalated privilege and view sensitive information via the httptrace interface.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37304
- https://github.com/jeecgboot/jeecg-boot/issues/2793
- https://github.com/jeecgboot/jeecg-boot
