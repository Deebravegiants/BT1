# [H] CVE-2022-48338

## Summary
Severity: High
Advisory: CVE-2022-48338
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-02-20
Source: https://osv.dev/vulnerability/CVE-2022-48338
Type: osv

## Details
An issue was discovered in GNU Emacs through 28.2. In ruby-mode.el, the ruby-find-library-file function has a local command injection vulnerability. The ruby-find-library-file function is an interactive function, and bound to C-c C-f. Inside the function, the external command gem is called through shell-command-to-string, but the feature-name parameters are not escaped. Thus, malicious Ruby source files may cause commands to be executed.

## References
- https://git.savannah.gnu.org/cgit/emacs.git/commit/?id=9a3b08061feea14d6f37685ca1ab8801758bfd1c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48338.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FLPQ4K6H2S5TY3L5UDN4K4B3L5RQJYQ6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U6HDBUQNAH2WL4MHWCTUZLN7NGF7CHTK/
- https://nvd.nist.gov/vuln/detail/CVE-2022-48338
- https://www.debian.org/security/2023/dsa-5360
