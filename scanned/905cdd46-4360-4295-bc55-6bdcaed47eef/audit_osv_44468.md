# [M] AshAi tool loop never terminates when all tool calls are filtered out, enabling denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-82579
Aliases: EEF-CVE-2026-82579, GHSA-rcx7-x2w5-mmc2
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82579
Type: osv

## Details
Loop with Unreachable Exit Condition (Infinite Loop) vulnerability in ash-project ash_ai allows an attacker who can influence a model's output to hang the tool loop and drive unbounded, repeated model requests.

AshAi.ToolLoop classifies a model response of :tool_calls, then filters the calls through normalize_tool_calls/2 and unprocessed_tool_calls/2. Both can empty the list: a call missing a valid name, or one reusing a tool_call_id that already has a result in history, is dropped. With an empty list the loop appended nothing and recursed with a byte-identical message list, so the conversation never advanced and the same request was re-sent every iteration. Under the supported max_iterations: :infinity this never terminated; otherwise it exhausted the full budget. Prompt-injected content can make the model re-emit a spent tool_call_id. The fix treats an empty post-filter list as terminal.

This issue affects ash_ai: from 0.6.0 before 1.0.0.

## References
- https://cna.erlef.org/cves/CVE-2026-82579.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82579
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82579.json
- https://github.com/ash-project/ash_ai/security/advisories/GHSA-rcx7-x2w5-mmc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-82579
- https://github.com/ash-project/ash_ai/commit/53325fdab90afab628c6a53232ef2a9001580bd9
- https://github.com/ash-project/ash_ai
