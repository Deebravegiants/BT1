# [H] CVE-2026-2291

## Summary
Severity: High
Advisory: CVE-2026-2291
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-2291
Type: osv

## Details
dnsmasqs extract_name() function can be abused to cause a heap buffer overflow, allowing an attacker to inject false DNS cache entries, which could result in DNS lookups to redirect to an attacker-controlled IP address, or to cause a DoS.

## References
- http://www.openwall.com/lists/oss-security/2026/07/20/14
- https://github.com/pi-hole/FTL/releases/tag/v6.6.2
- https://lists.thekelleys.org.uk/pipermail/dnsmasq-discuss/2026q2/018471.html
- https://thekelleys.org.uk/dnsmasq/CVE/
- https://www.kb.cert.org/vuls/id/471747
- https://www.suse.com/security/cve/CVE-2026-2291.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2291.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2291
- https://github.com/NixOS/nixpkgs/pull/519082
- https://github.com/NixOS/nixpkgs/pull/519093
