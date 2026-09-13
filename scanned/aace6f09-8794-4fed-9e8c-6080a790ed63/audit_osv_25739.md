# [M] Unchecked access to font glyph info in xrdp

## Summary
Severity: Medium
Advisory: CVE-2023-42822
Aliases: GHSA-2hjx-rm4f-r9hw
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N)
Published: 2023-09-27
Source: https://osv.dev/vulnerability/CVE-2023-42822
Type: osv

## Details
xrdp is an open source remote desktop protocol server. Access to the font glyphs in xrdp_painter.c is not bounds-checked . Since some of this data is controllable by the user, this can result in an out-of-bounds read within the xrdp executable. The vulnerability allows an out-of-bounds read within a potentially privileged process. On non-Debian platforms, xrdp tends to run as root. Potentially an out-of-bounds write can follow the out-of-bounds read. There is no denial-of-service impact, providing xrdp is running in forking mode. This issue has been addressed in release 0.9.23.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5FPGA4M7IYCP7OILDF2ZJEVSXUOFEFQ6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PFGL22QQF65OIZRMCKUZCVJQCKGUBRYE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RTXODUR4ILM7ZPA6ZGY6VSK4BBSBMKGY/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42822.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-2hjx-rm4f-r9hw
- https://nvd.nist.gov/vuln/detail/CVE-2023-42822
- https://github.com/neutrinolabs/xrdp/commit/73acbe1f7957c65122b00de4d6f57a8d0d257c40
