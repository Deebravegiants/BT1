# [M] CVE-2022-4415

## Summary
Severity: Medium
Advisory: CVE-2022-4415
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-11
Source: https://osv.dev/vulnerability/CVE-2022-4415
Type: osv

## Details
A vulnerability was found in systemd. This security flaw can cause a local information leak due to systemd-coredump not respecting the fs.suid_dumpable kernel setting.

## References
- http://seclists.org/fulldisclosure/2025/Jun/9
- https://www.openwall.com/lists/oss-security/2022/12/21/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4415.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4415
- https://security.netapp.com/advisory/ntap-20230216-0010/
- https://github.com/systemd/systemd/commit/b7641425659243c09473cd8fb3aef2c0d4a3eb9c
