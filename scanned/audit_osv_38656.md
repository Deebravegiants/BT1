# [M] mosparo: Rule package source URL stored SSRF enables internal HTTP probing

## Summary
Severity: Medium
Advisory: CVE-2026-41195
Aliases: GHSA-92fh-26qf-r8rg
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-41195
Type: osv

## Details
mosparo is the modern solution to protect your online forms from spam. Prior to 1.4.13, the automatic rule package source URL feature allows a project member with the editor role to store an attacker-controlled URL that the server later fetches. Because the server follows http/https redirects and does not restrict private or loopback destinations, this becomes a stored SSRF primitive that can be turned into an internal HTTP probing oracle. This vulnerability is fixed in 1.4.13.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41195.json
- https://github.com/mosparo/mosparo/security/advisories/GHSA-92fh-26qf-r8rg
- https://nvd.nist.gov/vuln/detail/CVE-2026-41195
