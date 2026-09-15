# [H] Bagisto is vulnerable to SSTI via name parameters provided by non-admin low-privilege users

## Summary
Severity: High
Advisory: GHSA-mqhg-v22x-pqj8
CVE: CVE-2026-21449
CWE: CWE-1336
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-mqhg-v22x-pqj8
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=0 <2.3.10

## Details
### Summary
SSTI is possible via first name and last name parameters provided by lowest-privileged users.
### Details
1. Go to `http://127.0.0.1:8000/` and login or signup 
2. Go to `http://127.0.0.1:8000/customer/account/profile`
3. Now edit the first name and last name to {{7*7}}
4. Notice it appears as 49

### POC
- Video attached with the report: https://github.com/user-attachments/assets/f93932b5-2a57-4f34-897e-4151a5168912

### Impact
This can lead to RCE, command injection.

## References
- https://github.com/bagisto/bagisto/security/advisories/GHSA-mqhg-v22x-pqj8
- https://nvd.nist.gov/vuln/detail/CVE-2026-21449
- https://github.com/bagisto/bagisto/commit/4144931da0014c696f9126132ce44d7cfbdb2761
- https://github.com/bagisto/bagisto
- https://github.com/bagisto/bagisto/releases/tag/v2.3.10
