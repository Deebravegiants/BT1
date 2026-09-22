# [M] CVE-2026-11604

## Summary
Severity: Medium
Advisory: CVE-2026-11604
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-11604
Type: osv

## Details
An incorrect buffer size calculation in the epoch key generator in OpenVPN ovpn-dco-win version 2.0.0 through 2.8.3 allows a remote authenticated peer to trigger a heap-based buffer overflow and kernel memory corruption via a crafted data packet, resulting in a system crash (denial of service).

## References
- https://community.openvpn.net/Security%20Announcements/CVE-2026-11604
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11604.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11604
- https://github.com/OpenVPN/ovpn-dco-win/releases
