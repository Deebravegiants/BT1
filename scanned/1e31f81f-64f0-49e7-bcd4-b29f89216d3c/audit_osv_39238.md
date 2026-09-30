# [M] OpenProject: Stored CSS injection via Sanitize::Config::RELAXED[:css] enables phishing overlays and data exfiltration

## Summary
Severity: Medium
Advisory: CVE-2026-44696
Aliases: GHSA-j9q2-49mp-hmq5
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-44696
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.4.0, OpenProject's rich text (markdown) rendering pipeline uses Sanitize::Config::RELAXED[:css] for inline style sanitization. This configuration permits essentially all CSS properties in style attributes on permitted HTML elements (figure, img, table, th, tr, td). This allows any authenticated user with write access to formattable text fields (work package descriptions, comments, project descriptions, news) to inject CSS This vulnerability is fixed in 17.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44696.json
- https://github.com/opf/openproject/security/advisories/GHSA-j9q2-49mp-hmq5
- https://nvd.nist.gov/vuln/detail/CVE-2026-44696
