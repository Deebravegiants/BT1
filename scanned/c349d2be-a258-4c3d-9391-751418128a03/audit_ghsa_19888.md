# [H] InvokeAI Uncontrolled Resource Consumption vulnerability

## Summary
Severity: High
Advisory: GHSA-ffh5-w482-c7m5
CVE: CVE-2024-11043
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-ffh5-w482-c7m5
Type: github-advisory

## Affected
- PyPI: `InvokeAI` — affected >=0

## Details
A Denial of Service (DoS) vulnerability was discovered in the /api/v1/boards/{board_id} endpoint of invoke-ai/invokeai version v5.0.2. This vulnerability occurs when an excessively large payload is sent in the board_name field during a PATCH request. By sending a large payload, the UI becomes unresponsive, rendering it impossible for users to interact with or manage the affected board. Additionally, the option to delete the board becomes inaccessible, amplifying the severity of the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11043
- https://github.com/invoke-ai/InvokeAI
- https://github.com/invoke-ai/InvokeAI/blob/b79f2a4e4f183db9016584813748a69d34d62a26/invokeai/app/services/shared/invocation_context.py#L76
- https://huntr.com/bounties/9270900a-b8b7-402f-aee5-432d891e5648
