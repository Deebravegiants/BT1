# [M] CVE-2026-13117

## Summary
Severity: Medium
Advisory: CVE-2026-13117
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-13117
Type: osv

## Details
An incomplete guard in OpenVPN 2.6.0 through 2.6.20 and 2.7_alpha1 through 2.7.4 allows remote authenticated peers to trigger a use-after-free during TLS session promotion, potentially leading to a denial of service or memory leakage

## References
- https://community.openvpn.net/ReleaseHistory#openvpn-2621-released-1-july-2026
- https://community.openvpn.net/ReleaseHistory#openvpn-275-released-1-july-2026
- https://community.openvpn.net/Security%20Announcements/CVE-2026-13117
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13117.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13117
