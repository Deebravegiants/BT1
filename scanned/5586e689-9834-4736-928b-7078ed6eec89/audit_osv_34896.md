# [C] OrangeHRM is Vulnerable to Account Takeover Through Unvalidated Username in Password Reset Workflow

## Summary
Severity: Critical
Advisory: CVE-2025-66225
Aliases: GHSA-5ghw-9775-v263
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-66225
Type: osv

## Details
OrangeHRM is a comprehensive human resource management (HRM) system. From version 5.0 to 5.7, the password reset workflow does not enforce that the username submitted in the final reset request matches the account for which the reset process was originally initiated. After obtaining a valid reset link for any account they can receive email for, an attacker can alter the username parameter in the final reset request to target a different user. Because the system accepts the supplied username without verification, the attacker can set a new password for any chosen account, including privileged accounts, resulting in full account takeover. This issue has been patched in version 5.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66225.json
- https://github.com/orangehrm/orangehrm/security/advisories/GHSA-5ghw-9775-v263
- https://nvd.nist.gov/vuln/detail/CVE-2025-66225
