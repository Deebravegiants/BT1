# [H] CVE-2021-3547

## Summary
Severity: High
Advisory: CVE-2021-3547
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-07-12
Source: https://osv.dev/vulnerability/CVE-2021-3547
Type: osv

## Details
OpenVPN 3 Core Library version 3.6 and 3.6.1 allows a man-in-the-middle attacker to bypass the certificate authentication by issuing an unrelated server certificate using the same hostname found in the verify-x509-name option in a client configuration.

## References
- https://community.openvpn.net/openvpn/wiki/SecurityAnnouncements
- https://community.openvpn.net/openvpn/wiki/CVE-2021-3547
