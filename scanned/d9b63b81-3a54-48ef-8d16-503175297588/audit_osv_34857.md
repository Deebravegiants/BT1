# [C] CVE-2025-65882

## Summary
Severity: Critical
Advisory: CVE-2025-65882
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-65882
Type: osv

## Details
An issue was discovered in openmptcprouter thru 0.64 in file common/package/utils/sys-upgrade-helper/src/tools/sysupgrade.c in function create_xor_ipad_opad allowing attackers to potentially write arbitrary files or execute arbitrary commands.

## References
- https://gist.github.com/AradCohen/939ee50d60c4d2bd555a364615a5ab9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65882.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65882
- https://github.com/Ysurac/openmptcprouter/commit/09393d1c41a227bea7d5b85c0a06221b1302b25f
