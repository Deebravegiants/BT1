# [M] text-generation-webui has a Path Traversal in load_prompt() — .txt file read without authentication

## Summary
Severity: Medium
Advisory: CVE-2026-35487
Aliases: GHSA-mfgg-vvc6-vqq7
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35487
Type: osv

## Details
text-generation-webui is an open-source web interface for running Large Language Models. Prior to 4.3, an unauthenticated path traversal vulnerability in load_prompt() allows reading any .txt file on the server filesystem. The file content is returned verbatim in the API response. This vulnerability is fixed in 4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35487.json
- https://github.com/oobabooga/text-generation-webui/security/advisories/GHSA-mfgg-vvc6-vqq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35487
