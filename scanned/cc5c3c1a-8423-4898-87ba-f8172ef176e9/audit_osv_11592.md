# [M] CVE-2017-8900

## Summary
Severity: Medium
Advisory: CVE-2017-8900
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-05-12
Source: https://osv.dev/vulnerability/CVE-2017-8900
Type: osv

## Details
LightDM through 1.22.0, when systemd is used in Ubuntu 16.10 and 17.x, allows physically proximate attackers to bypass intended AppArmor restrictions and visit the home directories of arbitrary users by establishing a guest session.

## References
- http://www.securityfocus.com/bid/98554
- https://launchpad.net/bugs/1663157
- https://people.canonical.com/~ubuntu-security/cve/2017/CVE-2017-8900.html
- https://www.ubuntu.com/usn/usn-3285-1/
