# [H] Vim for Windows Uncontrolled Search Path Element Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-66476
Aliases: GHSA-g77q-xrww-p834
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-02
Source: https://osv.dev/vulnerability/CVE-2025-66476
Type: osv

## Details
Vim is an open source, command line text editor. Prior to version 9.1.1947, an uncontrolled search path vulnerability on Windows allows Vim to execute malicious executables placed in the current working directory for the current edited file. On Windows, when using cmd.exe as a shell, Vim resolves external commands by searching the current working directory before system paths. When Vim invokes tools such as findstr for :grep, external commands or filters via :!, or compiler/:make commands, it may inadvertently run a malicious executable present in the same directory as the file being edited. The issue affects Vim for Windows prior to version 9.1.1947.

## References
- http://www.openwall.com/lists/oss-security/2025/12/02/5
- https://github.com/vim/vim/releases/tag/v9.1.1947
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66476.json
- https://github.com/vim/vim/security/advisories/GHSA-g77q-xrww-p834
- https://nvd.nist.gov/vuln/detail/CVE-2025-66476
- https://github.com/vim/vim/commit/083ec6d9a3b7b09006e0ce69ac802597d25
