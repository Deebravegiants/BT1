# [H] text-generation-webui has a Path Traversal in load_grammar() — arbitrary file read without authentication

## Summary
Severity: High
Advisory: CVE-2026-35485
Aliases: GHSA-hqg5-487v-5mc6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35485
Type: osv

## Details
text-generation-webui is an open-source web interface for running Large Language Models. Prior to 4.3, an unauthenticated path traversal vulnerability in load_grammar() allows reading any file on the server filesystem with no extension restriction. Gradio does not server-side validate dropdown values, so an attacker can POST directory traversal payloads (e.g., ../../../etc/passwd) via the API and receive the full file contents in the response. This vulnerability is fixed in 4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35485.json
- https://github.com/oobabooga/text-generation-webui/security/advisories/GHSA-hqg5-487v-5mc6
- https://nvd.nist.gov/vuln/detail/CVE-2026-35485
