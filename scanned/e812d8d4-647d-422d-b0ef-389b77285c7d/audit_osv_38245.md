# [M] text-generation-webui has a Path Traversal in load_preset() — .yaml file read without authentication

## Summary
Severity: Medium
Advisory: CVE-2026-35484
Aliases: GHSA-w3cv-4447-5hf5
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35484
Type: osv

## Details
text-generation-webui is an open-source web interface for running Large Language Models. Prior to 4.3, an unauthenticated path traversal vulnerability in load_preset() allows reading any .yaml file on the server filesystem. The parsed YAML key-value pairs (including passwords, API keys, connection strings) are returned in the API response. This vulnerability is fixed in 4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35484.json
- https://github.com/oobabooga/text-generation-webui/security/advisories/GHSA-w3cv-4447-5hf5
- https://nvd.nist.gov/vuln/detail/CVE-2026-35484
