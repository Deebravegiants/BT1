# [H] CVE-2024-22667

## Summary
Severity: High
Advisory: CVE-2024-22667
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2024-22667
Type: osv

## Details
Vim before 9.0.2142 has a stack-based buffer overflow because did_set_langmap in map.c calls sprintf to write to the error buffer that is passed down to the option callback functions.

## References
- https://gist.githubusercontent.com/henices/2467e7f22dcc2aa97a2453e197b55a0c/raw/7b54bccc9a129c604fb139266f4497ab7aaa94c7/gistfile1.txt
- https://lists.debian.org/debian-lts-announce/2025/03/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UI44Y4LJLG34D4HNB6NTPLUPZREHAEL7/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UIQLVUSYHDN3644K6EFDI7PRZOTIKXM3/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22667.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UI44Y4LJLG34D4HNB6NTPLUPZREHAEL7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UIQLVUSYHDN3644K6EFDI7PRZOTIKXM3/
- https://nvd.nist.gov/vuln/detail/CVE-2024-22667
- https://security.netapp.com/advisory/ntap-20240223-0008/
- https://github.com/vim/vim/commit/b39b240c386a5a29241415541f1c99e2e6b8ce47
