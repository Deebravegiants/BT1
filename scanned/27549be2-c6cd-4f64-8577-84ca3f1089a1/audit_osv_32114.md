# [M] CVE-2025-24531

## Summary
Severity: Medium
Advisory: CVE-2025-24531
Aliases: GHSA-7mf6-rg36-qgch
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/CVE-2025-24531
Type: osv

## Details
In OpenSC pam_pkcs11 before 0.6.13, pam_sm_authenticate() wrongly returns PAM_IGNORE in many error situations (such as an error triggered by a smartcard before login), allowing authentication bypass.

## References
- http://www.openwall.com/lists/oss-security/2025/02/06/3
- http://www.openwall.com/lists/oss-security/2025/02/06/7
- https://www.openwall.com/lists/oss-security/2025/02/06/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24531.json
- https://github.com/OpenSC/pam_pkcs11/security/advisories/GHSA-7mf6-rg36-qgch
- https://nvd.nist.gov/vuln/detail/CVE-2025-24531
- https://github.com/OpenSC/pam_pkcs11/releases
