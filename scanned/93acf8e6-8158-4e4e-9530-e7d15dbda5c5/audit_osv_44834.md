# [M] Snipe-IT before 8.7.0 Arbitrary File Read and SSRF via Markdown

## Summary
Severity: Medium
Advisory: CVE-2026-86751
Aliases: GHSA-f3vq-g24v-xc2g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86751
Type: osv

## Details
Snipe-IT before 8.7.0 fails to properly sanitize markdown image syntax in note fields, allowing authenticated users to read arbitrary server files and issue server-side HTTP requests. Attackers can submit markdown image syntax in checkout acceptance notes that survive HTML escaping, are expanded by CommonMark parser, and resolved by laravel-mail-auto-embed via file_get_contents or curl, exfiltrating sensitive files like .env containing APP_KEY.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86751.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-f3vq-g24v-xc2g
- https://nvd.nist.gov/vuln/detail/CVE-2026-86751
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-arbitrary-file-read-and-ssrf-via-markdown
