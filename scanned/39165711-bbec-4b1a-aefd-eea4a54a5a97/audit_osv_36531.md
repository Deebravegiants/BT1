# [H] Horilla HR has 2FA Bypass through its OTP Handling Logic

## Summary
Severity: High
Advisory: CVE-2026-24038
Aliases: GHSA-hqpv-ff5v-3hwf
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2026-24038
Type: osv

## Details
Horilla is a free and open source Human Resource Management System (HRMS). In version 1.4.0, the OTP handling logic has a flawed equality check that can be bypassed. When an OTP expires, the server returns None, and if an attacker omits the otp field from their POST request, the user-supplied OTP is also None, causing the comparison user_otp == otp to pass. This allows an attacker to bypass two-factor authentication entirely without ever providing a valid OTP. If administrative accounts are targeted, it could lead to compromise of sensitive HR data, manipulation of employee records, and further system-wide abuse. This issue has been fixed in version 1.5.0.

## References
- https://github.com/horilla-opensource/horilla/releases/tag/1.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24038.json
- https://github.com/horilla-opensource/horilla/security/advisories/GHSA-hqpv-ff5v-3hwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-24038
