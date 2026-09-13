# [M] Vvveb < 1.0.8.1 SSRF via oEmbedProxy

## Summary
Severity: Medium
Advisory: CVE-2026-34428
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-34428
Type: osv

## Details
Vvveb prior to 1.0.8.1 contains a server-side request forgery vulnerability in the oEmbedProxy action of the editor/editor module where the url parameter is passed directly to getUrl() via curl without scheme or destination validation. Authenticated backend users can supply file:// URLs to read arbitrary files readable by the web server process or http:// URLs targeting internal network addresses to probe internal services, with response bodies returned directly to the caller.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34428.json
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-34428
- https://www.vulncheck.com/advisories/vvveb-ssrf-via-oembedproxy
- https://github.com/givanz/Vvveb/commit/2d356844f37819bf771e7cd5e12a8686975e0b2b
- https://github.com/givanz/Vvveb
