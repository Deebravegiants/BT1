# [H] CVE-2026-30459

## Summary
Severity: High
Advisory: CVE-2026-30459
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-30459
Type: osv

## Details
An issue in the Forgot Password feature of Daylight Studio FuelCMS v1.5.2 allows unauthenticated attackers to obtain the password reset token of a victim user via a crafted link placed in a valid e-mail message.

## References
- https://github.com/daylightstudio/FUEL-CMS/blob/master/fuel/modules/fuel/controllers/Login.php
- https://pentest-tools.com/PTT-2025-029-Password-Reset-Poisoning-via-Host-Header.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30459.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30459
