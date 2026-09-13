# [H] CVE-2025-60954

## Summary
Severity: High
Advisory: CVE-2025-60954
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2025-10-24
Source: https://osv.dev/vulnerability/CVE-2025-60954
Type: osv

## Details
Microweber CMS 2.0 has Weak Password Requirements. The application does not enforce minimum password length or complexity during password resets. Users can set extremely weak passwords, including single-character passwords, which can lead to account compromise, including administrative accounts.

## References
- https://gist.github.com/progprnv/feae2b76f2db0cb2ac6e14b1bf7d8646
- https://github.com/progprnv/CVE-Reports/blob/main/CVE-2025-60954
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60954.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60954
- https://github.com/microweber/microweber
