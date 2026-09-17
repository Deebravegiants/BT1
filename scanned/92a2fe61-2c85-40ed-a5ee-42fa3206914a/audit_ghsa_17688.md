# [H] Claude Code Improper Authorization via websocket connections from arbitrary origins

## Summary
Severity: High
Advisory: GHSA-9f65-56v6-gxw7
CVE: CVE-2025-52882
CWE: CWE-1385, CWE-285
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2025-06-23
Source: https://github.com/advisories/GHSA-9f65-56v6-gxw7
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0.2.116 <1.0.24

## Details
Claude Code extensions in VSCode and forks (e.g., Cursor, Windsurf, and VSCodium) and JetBrains IDEs (e.g., IntelliJ, Pycharm, and Android Studio) are vulnerable to unauthorized websocket connections from an attacker when visiting attacker-controlled webpages. Claude Code for VSCode IDE extensions versions 0.2.116 through 1.0.23 are vulnerable. For Jetbrains IDE plugins, Claude Code [beta] versions 0.1.1 through 0.1.8 are vulnerable.  

In VSCode (and forks), exploitation would allow an attacker to read arbitrary files, see the list of files open in the IDE, get selection and diagnostics events from the IDE, or execute code in limited situations where a user has an open Jupyter Notebook and accepts a malicious prompt. In JetBrains IDEs, an attacker could get selection events, a list of open files, and a list of syntax errors.

**Remediation**

We released a patch for this issue on June 13th, 2025. Although Claude Code auto-updates when you launch it and auto-updates the extensions, you should take the following steps (the exact steps depend on your IDE).

**VSCode, Cursor, Windsurf, VSCodium, and other VSCode forks**
Extension Name: Claude Code for VSCode

Instructions:

1. Open the list of Extensions (View->Extensions)
2. Look for Claude Code for VSCode among installed extensions
3. If you have a version < 1.0.24, click “Update” (or “Uninstall”)
4. Restart the IDE 

**All JetBrains IDEs including IntelliJ, PyCharm, and Android Studio**
Plugin name: Claude Code [Beta]

Instructions:

1. Open the Plugins list
2. Look for Claude Code [Beta] among installed extensions
3. Update (or Uninstall) the plugin if the version is < 0.1.9
4. Restart the IDE

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-9f65-56v6-gxw7
- https://nvd.nist.gov/vuln/detail/CVE-2025-52882
- https://github.com/anthropics/claude-code
