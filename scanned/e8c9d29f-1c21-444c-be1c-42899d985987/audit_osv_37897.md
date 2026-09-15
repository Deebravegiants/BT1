# [M] Open Source Point of Sale has an IDOR in Password Change (Home)

## Summary
Severity: Medium
Advisory: CVE-2026-33730
Aliases: GHSA-mcc2-8rp2-q6ch
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33730
Type: osv

## Details
Open Source Point of Sale (opensourcepos) is a web based point of sale application written in PHP using CodeIgniter framework. Prior to version 3.4.2, an Insecure Direct Object Reference (IDOR) vulnerability allows an authenticated low-privileged user to access the password change functionality of other users, including administrators, by manipulating the `employee_id` parameter. The application does not verify object ownership or enforce authorization checks. Version 3.4.2 adds object-level authorization checks to validate that the current user owns the employee_id being accessed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33730.json
- https://github.com/opensourcepos/opensourcepos/security/advisories/GHSA-mcc2-8rp2-q6ch
- https://nvd.nist.gov/vuln/detail/CVE-2026-33730
- https://github.com/opensourcepos/opensourcepos/commit/ee4d44ed396097d6010c5490ab4fd7cfae694624
