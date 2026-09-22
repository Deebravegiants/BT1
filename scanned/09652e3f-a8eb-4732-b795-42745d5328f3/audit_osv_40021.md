# [M] CVE-2026-4893

## Summary
Severity: Medium
Advisory: CVE-2026-4893
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-4893
Type: osv

## Details
An information disclosure vulnerability in dnsmasq allows remote attackers to bypass source checks via a crafted DNS packet with RFC 7871 client subnet information.

## References
- https://github.com/pi-hole/FTL/releases/tag/v6.6.2
- https://lists.thekelleys.org.uk/pipermail/dnsmasq-discuss/2026q2/018471.html
- https://thekelleys.org.uk/dnsmasq/CVE/
- https://www.kb.cert.org/vuls/id/471747
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4893.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4893
- https://github.com/NixOS/nixpkgs/pull/519082
- https://github.com/NixOS/nixpkgs/pull/519093
