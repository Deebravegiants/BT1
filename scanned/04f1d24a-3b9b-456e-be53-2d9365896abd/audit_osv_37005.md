# [C] SPIP tickets < 4.3.3 Unauthenticated RCE

## Summary
Severity: Critical
Advisory: CVE-2026-27744
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27744
Type: osv

## Details
The SPIP tickets plugin versions prior to 4.3.3 contain an unauthenticated remote code execution vulnerability in the forum preview handling for public ticket pages. The plugin appends untrusted request parameters into HTML that is later rendered by a template using unfiltered environment rendering (#ENV**), which disables SPIP output filtering. As a result, an unauthenticated attacker can inject crafted content that is evaluated through SPIP's template processing chain, leading to execution of code in the context of the web server.

## References
- https://git.spip.net/spip-contrib-extensions/tickets
- https://plugins.spip.net/tickets
- https://blog.spip.net/Mise-a-jour-de-securite-sortie-de-SPIP-4-4-10.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27744.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27744
- https://www.vulncheck.com/advisories/spip-tickets-unauthenticated-rce
- https://git.spip.net/spip-contrib-extensions/tickets/-/commit/869935b6687822ed79ad5477626a664d8ea6dcf7
- https://chocapikk.com/posts/2026/spip-plugins-vulnerabilities/
