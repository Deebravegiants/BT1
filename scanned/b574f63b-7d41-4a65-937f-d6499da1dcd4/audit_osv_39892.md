# [H] NexTOR_IP_CHANGER has PATH Injection Leading to Arbitrary Command Execution

## Summary
Severity: High
Advisory: CVE-2026-48097
Aliases: GHSA-vx6r-vwjq-567w
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-48097
Type: osv

## Details
NexTor IP Changer is a command-line tool that leverages the Tor network to periodically rotate a user's IP address. Versions prior to 2.0.0 have a command execution vulnerability due to unsafe use of `shell=True` with commands that rely on executable resolution through the `PATH` environment variable. An attacker controlling the execution environment can place malicious executables such as sudo earlier in the `PATH`, resulting in execution of attacker-controlled code. Version 2.0.0 fixes the issue.

## References
- https://github.com/0x5t4l1n/NexTOR_IP_CHANGER/releases/tag/v2.0
- https://github.com/0x5t4l1n/NexTOR_IP_CHANGER/security/advisories/GHSA-vx6r-vwjq-567w
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48097.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48097
