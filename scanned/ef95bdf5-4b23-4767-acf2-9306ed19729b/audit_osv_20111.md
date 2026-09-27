# [C] CVE-2021-30502

## Summary
Severity: Critical
Advisory: CVE-2021-30502
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-25
Source: https://osv.dev/vulnerability/CVE-2021-30502
Type: osv

## Details
The unofficial vscode-ghc-simple (aka Simple Glasgow Haskell Compiler) extension before 0.2.3 for Visual Studio Code allows remote code execution via a crafted workspace configuration with replCommand.

## References
- https://github.com/dramforever/vscode-ghc-simple/blob/master/CHANGELOG.md#v023
- https://github.com/dramforever/vscode-ghc-simple/releases
- https://vuln.ryotak.me/advisories/38
- https://github.com/dramforever/vscode-ghc-simple/commit/bc7f6f0b857dade46ea51496d8bd1a4edef39b46
