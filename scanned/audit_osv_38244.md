# [M] text-generation-webui has a Path Traversal in load_template() — .jinja/.yaml/.yml file read without authentication

## Summary
Severity: Medium
Advisory: CVE-2026-35483
Aliases: GHSA-85fx-vw25-4c95
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35483
Type: osv

## Details
text-generation-webui is an open-source web interface for running Large Language Models. Prior to 4.3, an unauthenticated path traversal vulnerability in load_template() allows reading files with .jinja, .jinja2, .yaml, or .yml extensions from anywhere on the server filesystem. For .jinja files the content is returned verbatim; for .yaml files a parsed key is extracted. This vulnerability is fixed in 4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35483.json
- https://github.com/oobabooga/text-generation-webui/security/advisories/GHSA-85fx-vw25-4c95
- https://nvd.nist.gov/vuln/detail/CVE-2026-35483
