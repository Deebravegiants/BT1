# [C] CVE-2026-34714

## Summary
Severity: Critical
Advisory: CVE-2026-34714
Aliases: GHSA-2gmj-rpqf-pxvh
CVSS: 9.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-34714
Type: osv

## Details
Vim before 9.2.0272 allows code execution that happens immediately upon opening a crafted file in the default configuration, because %{expr} injection occurs with tabpanel lacking P_MLE.

## References
- http://www.openwall.com/lists/oss-security/2026/04/02/4
- http://www.openwall.com/lists/oss-security/2026/04/02/5
- http://www.openwall.com/lists/oss-security/2026/04/03/6
- https://github.com/vim/vim/releases/tag/v9.2.0272
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34714.json
- https://www.openwall.com/lists/oss-security/2026/03/30/3
- https://access.redhat.com/security/cve/CVE-2026-34714
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34714.json
- https://github.com/vim/vim/security/advisories/GHSA-2gmj-rpqf-pxvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-34714
- https://bugzilla.redhat.com/show_bug.cgi?id=2453139
- https://github.com/vim/vim/commit/664701eb7576edb7c7c7d9f2d600815ec1f43459
