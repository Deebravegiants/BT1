# [C] Cal.com Authentication Bypass via bad TOTP + password checks

## Summary
Severity: Critical
Advisory: CVE-2025-66489
Aliases: GHSA-9r3w-4j8q-pw98
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:N)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/CVE-2025-66489
Type: osv

## Details
Cal.com is open-source scheduling software. Prior to 5.9.8, A flaw in the login credentials provider allows an attacker to bypass password verification when a TOTP code is provided, potentially gaining unauthorized access to user accounts. This issue exists due to problematic conditional logic in the authentication flow. This vulnerability is fixed in 5.9.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66489.json
- https://github.com/calcom/cal.com/security/advisories/GHSA-9r3w-4j8q-pw98
- https://nvd.nist.gov/vuln/detail/CVE-2025-66489
