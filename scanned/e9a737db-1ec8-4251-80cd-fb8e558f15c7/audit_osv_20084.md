# [C] CVE-2021-30124

## Summary
Severity: Critical
Advisory: CVE-2021-30124
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/CVE-2021-30124
Type: osv

## Details
The unofficial vscode-phpmd (aka PHP Mess Detector) extension before 1.3.0 for Visual Studio Code allows remote attackers to execute arbitrary code via a crafted phpmd.command value in a workspace folder.

## References
- https://marketplace.visualstudio.com/items?itemName=ecodes.vscode-phpmd
- https://vuln.ryotak.me/advisories/25
- https://github.com/sandhje/vscode-phpmd/commit/c462bf5c6f0160d0199855d5f8ed76be8d9beac0
