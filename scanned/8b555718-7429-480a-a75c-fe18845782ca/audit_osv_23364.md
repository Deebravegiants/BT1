# [H] CVE-2022-48339

## Summary
Severity: High
Advisory: CVE-2022-48339
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-02-20
Source: https://osv.dev/vulnerability/CVE-2022-48339
Type: osv

## Details
An issue was discovered in GNU Emacs through 28.2. htmlfontify.el has a command injection vulnerability. In the hfy-istext-command function, the parameter file and parameter srcdir come from external input, and parameters are not escaped. If a file name or directory name contains shell metacharacters, code may be executed.

## References
- https://git.savannah.gnu.org/cgit/emacs.git/commit/?id=1b4dc4691c1f87fc970fbe568b43869a15ad0d4c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48339.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FLPQ4K6H2S5TY3L5UDN4K4B3L5RQJYQ6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U6HDBUQNAH2WL4MHWCTUZLN7NGF7CHTK/
- https://nvd.nist.gov/vuln/detail/CVE-2022-48339
- https://www.debian.org/security/2023/dsa-5360
- https://lists.debian.org/debian-lts-announce/2023/05/msg00008.html
