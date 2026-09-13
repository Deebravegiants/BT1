# [C] HKUDS OpenHarness Remote Command Execution via /bridge Slash Command

## Summary
Severity: Critical
Advisory: CVE-2026-7551
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-7551
Type: osv

## Details
HKUDS OpenHarness contains a remote code execution vulnerability in the /bridge slash command that allows remote senders accepted by configuration to execute arbitrary operating system commands. Attackers can invoke the /bridge spawn command with attacker-controlled command text that is forwarded to the bridge session manager and executed through the shared shell subprocess helper, allowing them to spawn shell sessions as the OpenHarness process user and access local files, credentials, workspace state, and repository contents.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7551.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-7551
- https://www.vulncheck.com/advisories/hkuds-openharness-remote-command-execution-via-bridge-slash-command
- https://github.com/HKUDS/OpenHarness/pull/208
- https://github.com/HKUDS/OpenHarness/commit/438e37309778e19060dfe7b172eb142e543c4cd6
