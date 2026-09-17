# [M] Vim Ex command injection in Vims NetBeans integration

## Summary
Severity: Medium
Advisory: CVE-2026-39881
Aliases: GHSA-mr87-rhgv-7pw6
CVSS: 5.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:H/A:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-39881
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0316, a command injection vulnerability in Vim's netbeans interface allows a malicious netbeans server to execute arbitrary Ex commands when Vim connects to it, via unsanitized strings in the defineAnnoType and specialKeys protocol messages. This vulnerability is fixed in 9.2.0316.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0316
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39881.json
- https://github.com/vim/vim/security/advisories/GHSA-mr87-rhgv-7pw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-39881
- https://github.com/vim/vim/commit/7ab76a86048ed492374ac6b19
