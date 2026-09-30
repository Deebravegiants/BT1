# [H] CVE-2019-16765

## Summary
Severity: High
Advisory: CVE-2019-16765
Aliases: GHSA-wf4x-8mpj-r42q
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-16765
Type: osv

## Details
If an attacker can get a user to open a specially prepared directory tree as a workspace in Visual Studio Code with the CodeQL extension active, arbitrary code of the attacker's choosing may be executed on the user's behalf. This is fixed in version 1.0.1 of the extension. Users should upgrade to this version using Visual Studio Code Marketplace's upgrade mechanism. After upgrading, the codeQL.cli.executablePath setting can only be set in the per-user settings, and not in the per-workspace settings. More information about VS Code settings can be found here.

## References
- https://github.com/github/vscode-codeql/blob/v1.0.1/CHANGELOG.md
- https://github.com/github/vscode-codeql/security/advisories/GHSA-wf4x-8mpj-r42q
- https://github.com/github/vscode-codeql/pull/174
