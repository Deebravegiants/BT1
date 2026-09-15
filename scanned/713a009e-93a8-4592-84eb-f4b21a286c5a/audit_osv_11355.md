# [M] CVE-2017-7521

## Summary
Severity: Medium
Advisory: CVE-2017-7521
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-27
Source: https://osv.dev/vulnerability/CVE-2017-7521
Type: osv

## Details
OpenVPN versions before 2.4.3 and before 2.3.17 are vulnerable to remote denial-of-service due to memory exhaustion caused by memory leaks and double-free issue in extract_x509_extension().

## References
- http://www.securitytracker.com/id/1038768
- http://www.debian.org/security/2017/dsa-3900
- http://www.securityfocus.com/bid/99230
- https://community.openvpn.net/openvpn/wiki/VulnerabilitiesFixedInOpenVPN243
