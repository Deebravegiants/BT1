# [M] CodeWhale before 0.8.64 SSRF Bypass via DNS Pinning TOCTOU

## Summary
Severity: Medium
Advisory: CVE-2026-75856
Aliases: GHSA-6v2g-fpxh-pmmh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75856
Type: osv

## Details
CodeWhale before 0.8.64 contains a server-side request forgery bypass vulnerability in DNS pinning logic that fails to prevent time-of-check-time-of-use attacks. Attackers can manipulate DNS responses to fail initial resolution checks and succeed on secondary requests, allowing requests to internal IP addresses and bypassing SSRF mitigations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75856.json
- https://github.com/Hmbown/CodeWhale/security/advisories/GHSA-6v2g-fpxh-pmmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-75856
- https://www.vulncheck.com/advisories/codewhale-before-ssrf-bypass-via-dns-pinning-toctou
- https://github.com/Hmbown/CodeWhale/commit/26de44a8bd5051f8f944ea60b2c37ae1d2b7d25e
