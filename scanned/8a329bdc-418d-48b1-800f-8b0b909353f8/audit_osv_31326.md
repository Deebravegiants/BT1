# [H] Unrestricted File Write and Read in composiohq/composio

## Summary
Severity: High
Advisory: CVE-2024-8958
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-8958
Type: osv

## Details
In composiohq/composio version 0.4.3, there is an unrestricted file write and read vulnerability in the filetools actions. Due to improper validation of file paths, an attacker can read and write files anywhere on the server, potentially leading to privilege escalation or remote code execution.

## References
- https://huntr.com/bounties/e152b094-0593-428e-b813-068d2390ce68
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8958.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8958
