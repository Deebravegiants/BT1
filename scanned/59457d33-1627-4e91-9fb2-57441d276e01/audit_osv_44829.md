# [M] Snipe-IT before 8.7.0 Arbitrary File Read and SSRF via Category EULA

## Summary
Severity: Medium
Advisory: CVE-2026-86741
Aliases: GHSA-qmhc-p47c-6x75
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86741
Type: osv

## Details
Snipe-IT versions before 8.7.0 fail to sanitize the category EULA text field before rendering it in checkout confirmation emails. Attackers with low-privilege permissions can inject markdown image syntax or raw HTML img tags pointing to local files or remote URLs, which the mail auto-embed library resolves server-side and returns as email attachments, exfiltrating sensitive files like .env credentials and enabling SSRF attacks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86741.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-qmhc-p47c-6x75
- https://nvd.nist.gov/vuln/detail/CVE-2026-86741
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-arbitrary-file-read-and-ssrf-via-category-eula
