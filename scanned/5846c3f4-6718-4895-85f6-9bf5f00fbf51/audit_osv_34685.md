# [H] CVE-2025-63800

## Summary
Severity: High
Advisory: CVE-2025-63800
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-63800
Type: osv

## Details
The password change endpoint in Open Source Point of Sale 3.4.1 allows users to set their account password to an empty string due to missing server-side validation. When an authenticated user omits or leaves the `password` and `repeat_password` parameters empty in the password change request, the backend still returns a successful response and sets the password to an empty string. This effectively disables authentication and may allow unauthorized access to user or administrative accounts.

## References
- https://github.com/omkaryepre/vulnerability-research/tree/main/CVE-2025-63800
- https://opensourcepos.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63800.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63800
- https://github.com/opensourcepos/opensourcepos
