# [C] CVE-2016-9470

## Summary
Severity: Critical
Advisory: CVE-2016-9470
CVSS: 9.0 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2017-03-28
Source: https://osv.dev/vulnerability/CVE-2016-9470
Type: osv

## Details
Revive Adserver before 3.2.5 and 4.0.0 suffers from Reflected File Download. `www/delivery/asyncspc.php` was vulnerable to the fairly new Reflected File Download (RFD) web attack vector that enables attackers to gain complete control over a victim's machine by virtually downloading a file from a trusted domain.

## References
- https://hackerone.com/reports/148745
- https://github.com/revive-adserver/revive-adserver/commit/69aacbd2
- https://www.revive-adserver.com/security/revive-sa-2016-002/
