# [M] Hugo: XSS via unescaped code-fence language in default code block renderer

## Summary
Severity: Medium
Advisory: GHSA-q76j-gcg9-vxc6
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-q76j-gcg9-vxc6
Type: github-advisory

## Affected
- Go: `github.com/gohugoio/hugo` — affected >=0.60.0 <0.163.3

## Details
Hugo's default code-block renderer wrote the Markdown code-fence language / info-string into the `<code class="language-…" data-lang="…">` wrapper without HTML escaping. A fence info-string containing a quote and a `<script>` payload breaks out of the attribute and injects a live script element.

This is not an issue if you fully trust every file under /content and every content adapter you load.

## References
- https://github.com/gohugoio/hugo/security/advisories/GHSA-q76j-gcg9-vxc6
- https://github.com/gohugoio/hugo
