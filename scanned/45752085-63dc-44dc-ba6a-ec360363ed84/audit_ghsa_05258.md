# [M] n8n: Denial of Service via ZIP decompression in webhook workflow

## Summary
Severity: Medium
Advisory: GHSA-jqpw-qww5-cj4c
CVE: CVE-2026-54314
CWE: CWE-409
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-jqpw-qww5-cj4c
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.24.0

## Details
## Impact
The Compression node's Decompress operation expanded attacker-controlled archives into memory without enforcing limits on decompressed output size. An unauthenticated attacker could send a small compressed archive to a public webhook workflow using this node, causing the n8n process to terminate due to memory exhaustion and disrupting all workflows in the same instance. 

## Patches
The issue has been fixed in n8n version 2.24.0. Users should upgrade to this version or later to remediate the vulnerability. The fix introduces configurable limits on decompressed output size (`N8N_COMPRESSION_NODE_MAX_DECOMPRESSED_SIZE_BYTES`) and ZIP entry count (`N8N_COMPRESSION_NODE_MAX_ZIP_ENTRIES`).

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable the Compression node by adding `n8n-nodes-base.compression` to the `NODES_EXCLUDE` environment variable.
- Restrict public webhook workflows that accept archive file uploads to authenticated endpoints only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-jqpw-qww5-cj4c
- https://nvd.nist.gov/vuln/detail/CVE-2026-54314
- https://github.com/n8n-io/n8n
