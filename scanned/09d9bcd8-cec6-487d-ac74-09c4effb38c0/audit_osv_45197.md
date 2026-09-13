# [H] libgit2 is a portable C implementation of the Git core methods provided as a linkable library with a...

## Summary
Severity: High
Advisory: JLSEC-2025-185
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-21
Source: https://osv.dev/vulnerability/JLSEC-2025-185
Type: osv

## Affected
- Julia: `LibGit2_jll` — affected >=1.4.3+0 <1.7.2+0

## Details
libgit2 is a portable C implementation of the Git core methods provided as a linkable library with a solid API, allowing to build Git functionality into your application. Using well-crafted inputs to `git_revparse_single` can cause the function to enter an infinite loop, potentially causing a Denial of Service attack in the calling application. The revparse function in `src/libgit2/revparse.c` uses a loop to parse the user-provided spec string. There is an edge-case during parsing that allows a bad actor to force the loop conditions to access arbitrary memory. Potentially, this could also leak memory if the extracted rev spec is reflected back to the attacker. As such, libgit2 versions before 1.4.0 are not affected. Users should upgrade to version 1.6.5 or 1.7.2.

## References
- https://github.com/libgit2/libgit2/commit/add2dabb3c16aa49b33904dcdc07cd915efc12fa
- https://github.com/libgit2/libgit2/releases/tag/v1.6.5
- https://github.com/libgit2/libgit2/releases/tag/v1.7.2
- https://github.com/libgit2/libgit2/security/advisories/GHSA-54mf-x2rh-hq9v
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4M3P7WIEPXNRLBINQRJFXUSTNKBCHYC7/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7CNDW3PF6NHO7OXNM5GN6WSSGAMA7MZE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S635BGHHZUMRPI7QOXOJ45QHDD5FFZ3S/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z6MXOX7I43OWNN7R6M54XLG6U5RXY244/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZGNHOEE2RBLH7KCJUPUNYG4CDTW4HTBT/
