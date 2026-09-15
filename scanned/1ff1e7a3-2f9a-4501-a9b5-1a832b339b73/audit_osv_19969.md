# [H] CVE-2021-28790

## Summary
Severity: High
Advisory: CVE-2021-28790
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-18
Source: https://osv.dev/vulnerability/CVE-2021-28790
Type: osv

## Details
The unofficial SwiftLint extension before 1.4.5 for Visual Studio Code allows remote attackers to execute arbitrary code by constructing a malicious workspace with a crafted swiftlint.path configuration value that triggers execution upon opening the workspace.

## References
- https://github.com/vknabel/vscode-swiftlint/releases/tag/1.4.5
- https://vuln.ryotak.me/advisories/12
