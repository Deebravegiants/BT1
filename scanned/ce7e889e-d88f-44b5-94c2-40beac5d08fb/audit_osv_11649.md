# [H] CVE-2017-9217

## Summary
Severity: High
Advisory: CVE-2017-9217
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-24
Source: https://osv.dev/vulnerability/CVE-2017-9217
Type: osv

## Details
systemd-resolved through 233 allows remote attackers to cause a denial of service (daemon crash) via a crafted DNS response with an empty question section.

## References
- http://www.securityfocus.com/bid/98677
- https://security.netapp.com/advisory/ntap-20241213-0003/
- https://launchpad.net/bugs/1621396
- https://github.com/systemd/systemd/commit/a924f43f30f9c4acaf70618dd2a055f8b0f166be
- https://github.com/systemd/systemd/pull/5998
