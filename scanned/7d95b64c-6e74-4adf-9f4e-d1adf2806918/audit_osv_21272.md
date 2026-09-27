# [M] CVE-2021-41583

## Summary
Severity: Medium
Advisory: CVE-2021-41583
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-24
Source: https://osv.dev/vulnerability/CVE-2021-41583
Type: osv

## Details
vpn-user-portal (aka eduVPN or Let's Connect!) before 2.3.14, as packaged for Debian 10, Debian 11, and Fedora, allows remote authenticated users to obtain OS filesystem access, because of the interaction of QR codes with an exec that uses the -r option. This can be leveraged to obtain additional VPN access.

## References
- https://github.com/eduvpn/vpn-user-portal/releases
- https://list.surfnet.nl/pipermail/eduvpn-deploy/2021-September/000352.html
