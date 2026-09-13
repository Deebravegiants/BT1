# [H] CVE-2021-41171

## Summary
Severity: High
Advisory: CVE-2021-41171
Aliases: GHSA-q67h-5pc3-g6jv
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-22
Source: https://osv.dev/vulnerability/CVE-2021-41171
Type: osv

## Details
eLabFTW is an open source electronic lab notebook manager for research teams. In versions of eLabFTW before 4.1.0, it allows attackers to bypass a brute-force protection mechanism by using many different forged PHPSESSID values in HTTP Cookie header. This issue has been addressed by implementing brute force login protection, as recommended by Owasp with Device Cookies. This mechanism will not impact users and will effectively thwart any brute-force attempts at guessing passwords. The only correct way to address this is to upgrade to version 4.1.0. Adding rate limitation upstream of the eLabFTW service is of course a valid option, with or without upgrading.

## References
- https://github.com/elabftw/elabftw/releases/tag/4.1.0
- https://github.com/elabftw/elabftw/security/advisories/GHSA-q67h-5pc3-g6jv
- https://owasp.org/www-community/Slow_Down_Online_Guessing_Attacks_with_Device_Cookies
- https://github.com/elabftw/elabftw/commit/8e92afeec4c3a68dc88333881b7e6307f425706b
- https://www.exploit-db.com/docs/50436
