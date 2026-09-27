# [M] CVE-2023-7207

## Summary
Severity: Medium
Advisory: CVE-2023-7207
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/CVE-2023-7207
Type: osv

## Details
Debian's cpio contains a path traversal vulnerability. This issue was introduced by reverting CVE-2015-1197 patches which had caused a regression in --no-absolute-filenames. Upstream has since provided a proper fix to --no-absolute-filenames.

## References
- http://www.openwall.com/lists/oss-security/2024/01/05/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/7xxx/CVE-2023-7207.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-7207
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1059163
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-7207
- https://git.savannah.gnu.org/cgit/cpio.git/commit/?id=376d663340a9dc91c91a5849e5713f07571c1628
- https://www.openwall.com/lists/oss-security/2023/12/21/8
