# [M] CVE-2024-34055

## Summary
Severity: Medium
Advisory: CVE-2024-34055
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-05
Source: https://osv.dev/vulnerability/CVE-2024-34055
Type: osv

## Details
Cyrus IMAP before 3.8.3 and 3.10.x before 3.10.0-rc1 allows authenticated attackers to cause unbounded memory allocation by sending many LITERALs in a single command.

## References
- https://www.cyrusimap.org/dev/imap/download/release-notes/3.10/x/3.10.0-rc1.html
- https://www.cyrusimap.org/imap/download/release-notes/3.8/x/3.8.3.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34055.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CJZQAE3XC2GBCE5KSTWJ5A6QYANFWGFB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WVZHUZDU4MGTTZJRNACTMSKXLNMMRLJ6/
- https://nvd.nist.gov/vuln/detail/CVE-2024-34055
- https://github.com/cyrusimap/cyrus-imapd/commit/ef9e4e8314d6a06f2269af0ccf606894cc3fe489
