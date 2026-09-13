# [M] CVE-2026-11771

## Summary
Severity: Medium
Advisory: CVE-2026-11771
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-11771
Type: osv

## Details
OpenVPN version 2.1.0 through 2.6.20 and 2.7_alpha1 through 2.7.4 allows attackers via an off-by-one buffer write in the NTLM proxy authentication to potentially cause a crash via a crafted NTLM response from a malicious proxy server

## References
- https://community.openvpn.net/ReleaseHistory#openvpn-2621-released-1-july-2026
- https://community.openvpn.net/ReleaseHistory#openvpn-275-released-1-july-2026
- https://community.openvpn.net/Security%20Announcements/CVE-2026-11771
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11771.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11771
