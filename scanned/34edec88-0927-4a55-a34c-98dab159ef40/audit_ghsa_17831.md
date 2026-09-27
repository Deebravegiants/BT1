# [M] Composio Command Execution vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8h93-28hg-fj84
CVE: CVE-2024-53526
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-08
Source: https://github.com/advisories/GHSA-8h93-28hg-fj84
Type: github-advisory

## Affected
- PyPI: `composio-claude` — affected >=0.5.40 <0.6.9
- PyPI: `composio-openai` — affected >=0.5.40 <0.6.9
- PyPI: `composio-julep` — affected >=0.5.40 <0.6.9

## Details
composio >=0.5.40 is vulnerable to Command Execution in composio_openai, composio_claude, and composio_julep via the handle_tool_calls function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53526
- https://github.com/ComposioHQ/composio/issues/1073
- https://github.com/ComposioHQ/composio/pull/1107
- https://github.com/ComposioHQ/composio/commit/f496f7fa776335ae7825cad2991c9b38923271fc
- https://github.com/ComposioHQ/composio
- https://github.com/ComposioHQ/composio/blob/11ee7470aa6543097ee30bb036af8e9726dc7a85/python/plugins/claude/composio_claude/toolset.py#L156
- https://github.com/ComposioHQ/composio/blob/11ee7470aa6543097ee30bb036af8e9726dc7a85/python/plugins/julep/composio_julep/toolset.py#L21
- https://github.com/ComposioHQ/composio/blob/11ee7470aa6543097ee30bb036af8e9726dc7a85/python/plugins/openai/composio_openai/toolset.py#L184
