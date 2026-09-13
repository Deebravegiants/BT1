# [C] CryptoLib's Crypto_TC_ApplySecurity() Has a Heap Buffer Overflow Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-29909
Aliases: GHSA-q2pc-c3jx-3852
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-17
Source: https://osv.dev/vulnerability/CVE-2025-29909
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. In versions 1.3.3 and prior, a heap buffer overflow vulnerability in CryptoLib's `Crypto_TC_ApplySecurity()` allows an attacker to craft a malicious TC frame that causes out-of-bounds memory writes. This can result in denial of service (DoS) or, under certain conditions, remote code execution (RCE). Any application or system that relies on CryptoLib for Telecommand (TC) processing and does not strictly validate incoming TC frames is at risk. This includes satellite ground stations or mission control software where attackers can inject malformed frames. A patch is available at commit c7e8a8745ff4b5e9bd7e500e91358e86d5abedcc.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29909.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-q2pc-c3jx-3852
- https://nvd.nist.gov/vuln/detail/CVE-2025-29909
- https://github.com/nasa/CryptoLib/commit/c7e8a8745ff4b5e9bd7e500e91358e86d5abedcc
