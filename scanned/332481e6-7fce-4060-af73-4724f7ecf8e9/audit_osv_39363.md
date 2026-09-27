# [H] OS Command Injection in Microsoft UFO Shell Action Replay via Stored Session JSON

## Summary
Severity: High
Advisory: CVE-2026-45322
Aliases: GHSA-wj72-7w8h-695f
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45322
Type: osv

## Details
Microsoft UFO open-source framework for intelligent automation across devices and platforms. Microsoft UFO tagged releases up to and including v3.0.0 contain an OS command injection vulnerability in the shell action replay path. In affected releases, ShellReceiver.run_shell() passes a command string from action parameters directly to subprocess.Popen() with shell=True and executable=powershell.exe. The same shell-execution behavior is also reachable through ShellReceiver.execute_command(). The shell receiver is invoked by action classes such as RunShellCommand.execute() and ExecuteCommand.execute(), which forward stored action parameters to the shell receiver. Because UFO stores planned and executed actions in per-session JSON records, an attacker who can write or modify a session/action JSON file can plant a shell action. When the session is resumed or replayed, UFO executes the attacker's command as the UFO process user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45322.json
- https://github.com/microsoft/UFO/security/advisories/GHSA-wj72-7w8h-695f
- https://nvd.nist.gov/vuln/detail/CVE-2026-45322
