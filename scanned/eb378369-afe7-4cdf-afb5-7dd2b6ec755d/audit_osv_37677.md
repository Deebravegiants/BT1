# [M] AnythingLLM has a Zip Slip Path Traversal and Code Execution via Community Hub Plugin Import

## Summary
Severity: Medium
Advisory: CVE-2026-32719
Aliases: GHSA-rh66-4w74-cf4m
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32719
Type: osv

## Details
AnythingLLM is an application that turns pieces of content into context that any LLM can use as references during chatting. In 1.11.1 and earlier, The ImportedPlugin.importCommunityItemFromUrl() function in server/utils/agents/imported.js downloads a ZIP file from a community hub URL and extracts it using AdmZip.extractAllTo() without validating file paths within the archive. This enables a Zip Slip path traversal attack that can lead to arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32719.json
- https://github.com/Mintplex-Labs/anything-llm/security/advisories/GHSA-rh66-4w74-cf4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-32719
- https://github.com/Mintplex-Labs/anything-llm/commit/6a492f038da195a5c9a239d5ca2e9f2151c25f8c
