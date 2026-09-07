# [H] Git LFS may write to arbitrary files via crafted symlinks

## Summary
Severity: High
Advisory: GHSA-6pvw-g552-53c5
CVE: CVE-2025-26625
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-17
Source: https://github.com/advisories/GHSA-6pvw-g552-53c5
Type: github-advisory

## Affected
- Go: `github.com/git-lfs/git-lfs` — affected >=0.5.2 <3.7.1

## Details
### Impact

When populating a Git repository's working tree with the contents of Git LFS objects, certain Git LFS commands may write to files visible outside the current Git working tree if symbolic or hard links exist which collide with the paths of files tracked by Git LFS.

Git LFS has resolved this problem by revising the `git lfs checkout` and `git lfs pull` commands so that they check for symbolic links in the same manner as performed by Git before writing to files in the working tree.  These commands now also remove existing files in the working tree before writing new files in their place.

As well, Git LFS has resolved a problem whereby the `git lfs checkout` and `git lfs pull` commands, when run in a bare repository, could write to files visible outside the repository.  While a specific and relatively unlikely set of conditions were required for this to occur, it is no longer possible under any circumstances.

### Patches

This problem exists in all versions since 0.5.2 and is patched in v3.7.1.  All users should upgrade to v3.7.1.

### Workarounds

Support for symlinks in Git may be disabled by setting the `core.symlinks` configuration option to `false`, after which further clones and fetches will not create symbolic links.  However, any symbolic or hard links in existing repositories will still provide the opportunity for Git LFS to write to their targets.

### References

- https://github.com/git-lfs/git-lfs/security/advisories/GHSA-6pvw-g552-53c5
- https://nvd.nist.gov/vuln/detail/CVE-2025-26625
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-26625
- https://github.com/git-lfs/git-lfs/releases/tag/v3.7.1
- [git-lfs/git-lfs@5c11ffce9a](https://github.com/git-lfs/git-lfs/commit/5c11ffce9a4f095ff356bc781e2a031abb46c1a8)
- [git-lfs/git-lfs@0cffe93176](https://github.com/git-lfs/git-lfs/commit/0cffe93176b870055c9dadbb3cc9a4a440e98396)
- [git-lfs/git-lfs@d02bd13f02](https://github.com/git-lfs/git-lfs/commit/d02bd13f02ef76f6807581cd6b34709069cb3615)

### For more information

If there are any questions or comments about this advisory:
* For general questions, start a discussion in the Git LFS [discussion forum](https://github.com/git-lfs/git-lfs/discussions).
* For reports of additional vulnerabilities, please follow the Git LFS [security reporting policy](https://github.com/git-lfs/git-lfs/blob/main/SECURITY.md).

## References
- https://github.com/git-lfs/git-lfs/security/advisories/GHSA-6pvw-g552-53c5
- https://nvd.nist.gov/vuln/detail/CVE-2025-26625
- https://github.com/git-lfs/git-lfs/commit/0cffe93176b870055c9dadbb3cc9a4a440e98396
- https://github.com/git-lfs/git-lfs/commit/5c11ffce9a4f095ff356bc781e2a031abb46c1a8
- https://github.com/git-lfs/git-lfs/commit/d02bd13f02ef76f6807581cd6b34709069cb3615
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-26625
- https://github.com/git-lfs/git-lfs
- https://github.com/git-lfs/git-lfs/releases/tag/v3.7.1
- https://lists.debian.org/debian-lts-announce/2026/05/msg00055.html
