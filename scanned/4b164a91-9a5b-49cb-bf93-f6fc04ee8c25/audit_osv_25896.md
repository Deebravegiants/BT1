# [H] CVE-2023-46849

## Summary
Severity: High
Advisory: CVE-2023-46849
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-11
Source: https://osv.dev/vulnerability/CVE-2023-46849
Type: osv

## Details
Using the --fragment option in certain configuration setups OpenVPN version 2.6.0 to 2.6.6 allows an attacker to trigger a divide by zero behaviour which could cause an application crash, leading to a denial of service.

## References
- https://community.openvpn.net/openvpn/wiki/CVE-2023-46849
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L3FS46ANNTAVLIQY56ZKGM5CBTRVBUNE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/O54I7D753V6PU6XBU26FEROD2DSHEJQ4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46849.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-46849
- https://openvpn.net/security-advisory/access-server-security-update-cve-2023-46849-cve-2023-46850/
- https://www.debian.org/security/2023/dsa-5555
