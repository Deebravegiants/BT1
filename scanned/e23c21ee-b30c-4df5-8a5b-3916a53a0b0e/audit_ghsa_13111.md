# [H] Jeecg boot arbitrary file read vulnerability

## Summary
Severity: High
Advisory: GHSA-pm8v-ppx7-8hr4
CVE: CVE-2023-41578
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-08
Source: https://github.com/advisories/GHSA-pm8v-ppx7-8hr4
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-parent` — affected >=0

## Details
Jeecg boot up to v3.5.3 was discovered to contain an arbitrary file read vulnerability via the interface `/testConnection`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41578
- https://github.com/Snakinya/Bugs/issues/1
- https://github.com/jeecgboot/jeecg-boot
