# [M] CVE-2020-37173

## Summary
Severity: Medium
Advisory: CVE-2020-37173
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2020-37173
Type: osv

## Details
AVideo Platform 8.1 contains an information disclosure vulnerability that allows attackers to enumerate user details through the playlistsFromUser.json.php endpoint. Attackers can retrieve sensitive user information including email, password hash, and administrative status by manipulating the users_id parameter.

## References
- https://avideo.com
- https://www.vulncheck.com/advisories/avideo-platform-information-disclosure-user-enumeration
- https://github.com/WWBN/AVideo
- https://www.exploit-db.com/exploits/47997
