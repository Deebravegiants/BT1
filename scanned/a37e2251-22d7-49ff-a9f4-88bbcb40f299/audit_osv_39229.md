# [M] Zen Browser Mac - Address Bar Spoofing via Long Subdomain

## Summary
Severity: Medium
Advisory: CVE-2026-44659
Aliases: GHSA-7p2r-fp29-9w69
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-44659
Type: osv

## Details
Zen is a firefox-based browser. Prior to 1.19.12b, the ZEN Browser incorrectly truncates long hostnames in the address bar and shows only the attacker-controlled prefix of the subdomain, hiding the actual registrable domain (eTLD+1). As a result, an attacker can craft extremely long malicious subdomains that visually imitate trusted brands, and the browser will display only the spoofed prefix, misleading users about the actual origin of the site. This directly compromises the URL bar as a security indicator and creates a phishing/supply-chain attack vector. This vulnerability is fixed in 1.19.12b.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44659.json
- https://github.com/zen-browser/desktop/security/advisories/GHSA-7p2r-fp29-9w69
- https://nvd.nist.gov/vuln/detail/CVE-2026-44659
