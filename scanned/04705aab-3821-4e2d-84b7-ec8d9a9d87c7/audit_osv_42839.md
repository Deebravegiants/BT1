# [C] CyberPanel 2.4.3 Authenticated Command Injection via starRemoteTransfer

## Summary
Severity: Critical
Advisory: CVE-2026-71966
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-71966
Type: osv

## Details
CyberPanel 2.4.3, fixed in commit eca0c3c, contains an authenticated command injection vulnerability in the remote backup transfer feature that allows authenticated attackers to execute arbitrary OS commands by controlling a remote server's API response. Attackers can inject malicious commands through a crafted directory name in the remote server's API response, which bypasses security middleware validation and is passed unsanitized to the OS command execution function.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71966.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71966
- https://www.vulncheck.com/advisories/cyberpanel-authenticated-command-injection-via-starremotetransfer
- https://github.com/usmannasir/cyberpanel/commit/eca0c3cbeb35af8eaae9fafb094e8ef3cd923643
- https://github.com/usmannasir/cyberpanel
- https://themcsam.github.io/posts/cyberpanel-2.4.3-vulnerabilties/
