# [M] libgit2: Submodule path traversal

## Summary
Severity: Medium
Advisory: CVE-2026-53584
Aliases: GHSA-cw77-j82w-mchm
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-53584
Type: osv

## Details
libgit2 is a portable C implementation of the Git core methods provided as a linkable library with a solid API, allowing to build Git functionality into your application. Prior to 1.8.6 and 1.9.5, libgit2 does not reject traversal components in a submodule path loaded from .gitmodules. The affected src/libgit2/submodule.c paths include git_submodule_lookup and git_submodule_add_setup. A crafted repository can specify a path such as ../escape-target, and applications that initialize the submodule can create directories outside the repository working tree. This issue is fixed in versions 1.8.6 and 1.9.5.

## References
- https://github.com/libgit2/libgit2/releases/tag/v1.8.6
- https://github.com/libgit2/libgit2/releases/tag/v1.9.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53584.json
- https://github.com/libgit2/libgit2/security/advisories/GHSA-cw77-j82w-mchm
- https://nvd.nist.gov/vuln/detail/CVE-2026-53584
- https://github.com/libgit2/libgit2/commit/419637d3587396f5d139d6d88480eab3cd81e7a1
- https://github.com/libgit2/libgit2/commit/467c2d95ed663df722f83a5960edf568514b128c
- https://github.com/libgit2/libgit2/commit/ec7371da9f359cd8293e9108e7a0b1c1b61b67c4
