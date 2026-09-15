# [M] CVE-2026-35058

## Summary
Severity: Medium
Advisory: CVE-2026-35058
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-35058
Type: osv

## Details
Improper validation of packet length during tls-crypt-v2 key extraction in OpenVPN 2.6.0 through 2.6.19 and 2.7_alpha1 through 2.7.1 allows authenticated attackers to trigger a fatal assertion and cause a denial of service via a specially crafted packet.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2381
- https://community.openvpn.net/ReleaseHistory#openvpn-2620-released-22-april-2026
- https://community.openvpn.net/ReleaseHistory#openvpn-272-released-22-april-2026
- https://community.openvpn.net/Security%20Announcements/CVE-2026-35058
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35058.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-35058
