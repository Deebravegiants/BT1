# [C] gemini-mcp-tool vulnerable to OS command injection and @file exfiltration via prompt quoting (CVE-2026-0755)

## Summary
Severity: Critical
Advisory: GHSA-4h5r-5jm8-jxjm
CVE: CVE-2026-0755
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-4h5r-5jm8-jxjm
Type: github-advisory

## Affected
- npm: `gemini-mcp-tool` — affected >=1.1.2 <1.1.6

## Details
Untrusted prompt input could reach the Gemini CLI @file parser, allowing read/exfiltration of arbitrary local files (@/etc/passwd, @~/.ssh/id_rsa, @../../secret). On Windows, unquoted cmd.exe metacharacters could break out into OS command injection.

Fix (1.1.6): removed the broken shell:false double-quote wrapping; added assertSafeFileReferences() to contain @file refs to the working directory; hardened Windows cmd.exe argument quoting.

## References
- https://github.com/jamubc/gemini-mcp-tool/security/advisories/GHSA-4h5r-5jm8-jxjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-0755
- https://github.com/jamubc/gemini-mcp-tool
- https://www.zerodayinitiative.com/advisories/ZDI-26-021
