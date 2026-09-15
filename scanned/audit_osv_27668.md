# [H] libgit2 is vulnerable to arbitrary code execution due to heap corruption in `git_index_add`

## Summary
Severity: High
Advisory: CVE-2024-24577
Aliases: GHSA-j2v7-4f6v-gpg8
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2024-02-06
Source: https://osv.dev/vulnerability/CVE-2024-24577
Type: osv

## Details
libgit2 is a portable C implementation of the Git core methods provided as a linkable library with a solid API, allowing to build Git functionality into your application. Using well-crafted inputs to `git_index_add` can cause heap corruption that could be leveraged for arbitrary code execution. There is an issue in the `has_dir_name` function in `src/libgit2/index.c`, which frees an entry that should not be freed. The freed entry is later used and overwritten with potentially bad actor-controlled data leading to controlled heap corruption. Depending on the application that uses libgit2, this could lead to arbitrary code execution. This issue has been patched in version 1.6.5 and 1.7.2.

## References
- https://github.com/libgit2/libgit2/releases/tag/v1.6.5
- https://github.com/libgit2/libgit2/releases/tag/v1.7.2
- https://lists.debian.org/debian-lts-announce/2024/02/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4M3P7WIEPXNRLBINQRJFXUSTNKBCHYC7/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7CNDW3PF6NHO7OXNM5GN6WSSGAMA7MZE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S635BGHHZUMRPI7QOXOJ45QHDD5FFZ3S/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z6MXOX7I43OWNN7R6M54XLG6U5RXY244/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZGNHOEE2RBLH7KCJUPUNYG4CDTW4HTBT/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24577.json
- https://github.com/libgit2/libgit2/security/advisories/GHSA-j2v7-4f6v-gpg8
- https://nvd.nist.gov/vuln/detail/CVE-2024-24577
