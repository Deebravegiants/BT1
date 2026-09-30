# [M] FastGPT: workflow runtime can execute another user's private HTTP toolset

## Summary
Severity: Medium
Advisory: CVE-2026-61643
Aliases: GHSA-93r3-wqq3-c5ch
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-61643
Type: osv

## Details
FastGPT is a knowledge-based AI application platform. From 4.14.17 until 4.15.0-beta5, an authenticated FastGPT user can save a workflow node that points to another user's private HTTP toolset by using a crafted saved tool id such as http-<victim_toolset_app_id>/<tool_name>. The normal toolset routes deny access, but the workflow save and runtime path did not apply the same authorization check to the referenced toolset, allowing /api/v2/chat/completions to resolve the saved reference and execute the victim-owned HTTP tool. This issue is fixed in version 4.15.0-beta5.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.15.0-beta5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61643.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-93r3-wqq3-c5ch
- https://nvd.nist.gov/vuln/detail/CVE-2026-61643
