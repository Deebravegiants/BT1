# [H] CVE-2021-28792

## Summary
Severity: High
Advisory: CVE-2021-28792
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-18
Source: https://osv.dev/vulnerability/CVE-2021-28792
Type: osv

## Details
The unofficial Swift Development Environment extension before 2.12.1 for Visual Studio Code allows remote attackers to execute arbitrary code by constructing a malicious workspace with a crafted sourcekit-lsp.serverPath, swift.languageServerPath, swift.path.sourcekite, swift.path.sourcekiteDockerMode, swift.path.swift_driver_bin, or swift.path.shell configuration value that triggers execution upon opening the workspace.

## References
- https://github.com/vknabel/vscode-swift-development-environment/releases/tag/2.12.1
- https://vuln.ryotak.me/advisories/14
