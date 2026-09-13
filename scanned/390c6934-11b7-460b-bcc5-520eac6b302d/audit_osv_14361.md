# [H] CVE-2018-9336

## Summary
Severity: High
Advisory: CVE-2018-9336
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-01
Source: https://osv.dev/vulnerability/CVE-2018-9336
Type: osv

## Details
openvpnserv.exe (aka the interactive service helper) in OpenVPN 2.4.x before 2.4.6 allows a local attacker to cause a double-free of memory by sending a malformed request to the interactive service. This could cause a denial-of-service through memory corruption or possibly have unspecified other impact including privilege escalation.

## References
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2018&m=slackware-security.568761
- https://community.openvpn.net/openvpn/wiki/ChangesInOpenvpn24
- https://github.com/OpenVPN/openvpn/releases/tag/v2.4.6
- https://github.com/OpenVPN/openvpn/commit/1394192b210cb3c6624a7419bcf3ff966742e79b
- https://www.tenable.com/security/research/tra-2018-09
