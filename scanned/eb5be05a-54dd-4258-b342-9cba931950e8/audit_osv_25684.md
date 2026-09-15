# [M] Weak password of selenium VNC in MeterSphere

## Summary
Severity: Medium
Advisory: CVE-2023-41878
Aliases: GHSA-88vv-6rm4-59h9
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L)
Published: 2023-09-26
Source: https://osv.dev/vulnerability/CVE-2023-41878
Type: osv

## Details
MeterSphere is a one-stop open source continuous testing platform, covering functions such as test tracking, interface testing, UI testing and performance testing. The Selenium VNC config used in Metersphere is using a weak password by default, attackers can login to vnc and obtain high permissions. This issue has been addressed in version 2.10.7 LTS. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41878.json
- https://github.com/metersphere/metersphere/security/advisories/GHSA-88vv-6rm4-59h9
- https://nvd.nist.gov/vuln/detail/CVE-2023-41878
- https://github.com/metersphere/installer/commit/02dd31c0951a225eaad99eda560e3eb91ba3001d
