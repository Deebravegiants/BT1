# [H] Path traversal in github.com/ipfs/go-ipfs

## Summary
Severity: High
Advisory: GHSA-27pv-q55r-222g
CVE: CVE-2020-26279
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-27pv-q55r-222g
Type: github-advisory

## Affected
- Go: `github.com/ipfs/go-ipfs` — affected >=0 <0.8.0

## Details
### Impact
It is currently possible for path traversal to occur with DAGs containing relative paths during retrieval. This can cause files to be overwritten, or written to incorrect output directories. The issue can only occur when `ipfs get` is done on an affected DAG.

1. The only affected command is `ipfs get`.
2. The gateway is not affected.

### Patches
Traversal fix patched in https://github.com/whyrusleeping/tar-utils/commit/20a61371de5b51380bbdb0c7935b30b0625ac227
`tar-utils` patch applied to go-ipfs via https://github.com/ipfs/go-ipfs/commit/b7ddba7fe47dee5b1760b8ffe897908417e577b2

### Workarounds
Upgrade to go-ipfs 0.8 or later.

### References
Binaries for the patched versions of go-ipfs are available on the IPFS distributions site, https://dist.ipfs.io/go-ipfs

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [go-ipfs](https://github.com/ipfs/go-ipfs)
* Email us at [security@ipfs.io](mailto:security@ipfs.io)

## References
- https://github.com/ipfs/go-ipfs/security/advisories/GHSA-27pv-q55r-222g
- https://nvd.nist.gov/vuln/detail/CVE-2020-26279
- https://github.com/ipfs/go-ipfs/commit/b7ddba7fe47dee5b1760b8ffe897908417e577b2
- https://github.com/whyrusleeping/tar-utils/commit/20a61371de5b51380bbdb0c7935b30b0625ac227
