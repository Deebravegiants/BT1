# [M] snipe-it before 8.7.0 SSRF via IPv6 transition address bypass

## Summary
Severity: Medium
Advisory: CVE-2026-86735
Aliases: GHSA-5j6m-rr83-rpj7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86735
Type: osv

## Details
snipe-it versions before 8.7.0 contain a server-side request forgery vulnerability in the ExternalUrl validation rule that fails to detect IPv6 transition addresses encoding private IPv4 targets. Attackers with super-admin privileges can configure webhook URLs using NAT64, 6to4, or Teredo transition addresses to bypass SSRF guards and access internal services or cloud metadata endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86735.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-5j6m-rr83-rpj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-86735
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-ssrf-via-ipv6-transition-address-bypass
