# [H] OpenHands is Vulnerable to Command Injection through its Git Diff Handler

## Summary
Severity: High
Advisory: CVE-2026-33718
Aliases: GHSA-7h8w-hj9j-8rjw, PYSEC-2026-106
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33718
Type: osv

## Details
OpenHands is software for AI-driven development. Starting in version 1.5.0, a Command Injection vulnerability exists in the `get_git_diff()` method at `openhands/runtime/utils/git_handler.py:134`. The `path` parameter from the `/api/conversations/{conversation_id}/git/diff` API endpoint is passed unsanitized to a shell command, allowing authenticated attackers to execute arbitrary commands in the agent sandbox. The user is already allowed to instruct the agent to execute commands, but this bypasses the normal channels. Version 1.5.0 fixes the issue.

## References
- https://docs.python.org/3/library/shlex.html#shlex.quote
- https://docs.python.org/3/library/subprocess.html#security-considerations
- https://owasp.org/www-community/attacks/Command_Injection
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33718.json
- https://github.com/OpenHands/OpenHands/security/advisories/GHSA-7h8w-hj9j-8rjw
- https://nvd.nist.gov/vuln/detail/CVE-2026-33718
- https://github.com/OpenHands/OpenHands/pull/13051
