# [C] CtrlPanel: Unauthenticated RCE using installer script

## Summary
Severity: Critical
Advisory: CVE-2026-34234
Aliases: GHSA-jmhr-q9q5-fqwh
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-34234
Type: osv

## Details
CtrlPanel is open-source billing software for hosting providers. In versions 1.1.1 and prior, the web-based installer (public/installer/index.php) is vulnerable to unauthenticated Remote Code Execution (RCE) because it performs the install.lock check only after including and executing form handler files, leaving installer endpoints reachable on already-installed instances. The handlers also pass unsanitized user input directly into shell commands, allowing an attacker to submit crafted requests that execute arbitrary commands on the server. The vulnerability stems from two combined weaknesses: (1) premature form handler execution before the lock file gate, and (2) unsafe use of user input in shell command construction. This issue is reported to be actively exploited in the wild. The issue has been fixed in version 1.2.0.

## References
- https://github.com/Ctrlpanel-gg/panel/releases/tag/1.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34234.json
- https://github.com/Ctrlpanel-gg/panel/security/advisories/GHSA-jmhr-q9q5-fqwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-34234
