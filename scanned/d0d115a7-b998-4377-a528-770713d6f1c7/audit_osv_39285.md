# [M] AutoGPT: Credit system bypassed via direct block execution in POST /api/blocks/{block_id}/execute

## Summary
Severity: Medium
Advisory: CVE-2026-45023
Aliases: GHSA-8pjg-mfqm-vrhr
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-45023
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. Prior to 0.6.59, POST /api/blocks/{block_id}/execute endpoint executes blocks without consuming any credits, regardless of the user's balance. The credit check that exists in the graph execution path (manager.py) is never reached when blocks are called directly via the external API, allowing unlimited free execution of all blocks. This vulnerability is fixed in 0.6.59.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45023.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-8pjg-mfqm-vrhr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45023
