# [M] JLSEC-2026-1371

## Summary
Severity: Medium
Advisory: JLSEC-2026-1371
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/JLSEC-2026-1371
Type: osv

## Affected
- Julia: `LibGit2_jll` — affected >=0 <1.9.6+0

## Details
libgit2 is a portable C implementation of the Git core methods provided as a linkable library with a solid API, allowing to build Git functionality into your application. Prior to 1.8.6 and 1.9.5, `git_delta_apply` in `src/libgit2/delta.c` trusts the attacker-controlled `res_sz` value parsed by `hdr_sz` from a delta object header and passes that amount to `git__malloc` before validating delta instructions. Malicious pack data supplied through `git_clone`, `git_fetch`, `git_remote_fetch`, `git_indexer_append`, or a local attacker-supplied repository can use a very small multi-level `OFS_DELTA` chain to retain extremely large allocations and exhaust memory. This issue is fixed in versions 1.8.6 and 1.9.5.

## References
- https://github.com/libgit2/libgit2/commit/0cdfdd5fa8f8514c82413025e1e0808866cf7c30
- https://github.com/libgit2/libgit2/commit/c1896f06df22cc0ca5658df3a8f6cd7ede4cd6ae
- https://github.com/libgit2/libgit2/commit/dec22ac01ad9620c96b7b9ac3ef636ea46d43bed
- https://github.com/libgit2/libgit2/releases/tag/v1.8.6
- https://github.com/libgit2/libgit2/releases/tag/v1.9.5
- https://github.com/libgit2/libgit2/security/advisories/GHSA-27m5-gxxh-x79j
