# [C] Jeecg-Boot CMS arbitrary file upload vulnerability

## Summary
Severity: Critical
Advisory: GHSA-jf7x-57g8-9hm5
CVE: CVE-2020-28088
CWE: CWE-434
Ecosystem: Maven
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jf7x-57g8-9hm5
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-parent` — affected >=0

## Details
An arbitrary file upload vulnerability in `/jeecg-boot/sys/common/upload` of jeecg-boot CMS 2.3 allows attackers to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28088
- https://github.com/zhangdaiscott/jeecg-boot/issues/1888
- https://github.com/jeecgboot/jeecg-boot
