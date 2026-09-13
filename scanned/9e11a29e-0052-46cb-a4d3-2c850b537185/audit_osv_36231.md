# [M] Chainlit < 2.9.4 Arbitrary File Read via /project/element

## Summary
Severity: Medium
Advisory: CVE-2026-22218
Aliases: PYSEC-2026-598
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-22218
Type: osv

## Details
Chainlit versions prior to 2.9.4 contain an arbitrary file read vulnerability in the /project/element update flow. An authenticated client can send a custom Element with a user-controlled path value, causing the server to copy the referenced file into the attacker’s session. The resulting element identifier (chainlitKey) can then be used to retrieve the file contents via /project/file/<chainlitKey>, allowing disclosure of any file readable by the Chainlit service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22218.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22218
- https://www.vulncheck.com/advisories/chainlit-arbitrary-file-read-via-project-element
- https://github.com/Chainlit/chainlit/releases/tag/2.9.4
- https://github.com/Chainlit/chainlit
- https://www.zafran.io/resources/chainleak-critical-ai-framework-vulnerabilities-expose-data-enable-cloud-takeover
