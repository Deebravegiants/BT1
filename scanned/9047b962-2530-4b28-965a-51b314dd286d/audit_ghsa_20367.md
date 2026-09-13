# [H] Path Traversal in Git HTTP endpoints in Gogs

## Summary
Severity: High
Advisory: GHSA-6vcc-v9vw-g2x5
CVE: CVE-2022-1993
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-06-08
Source: https://github.com/advisories/GHSA-6vcc-v9vw-g2x5
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.9

## Details
### Impact

The malicious user is able to craft HTTP requests to access unauthorized Git directories. All installations with are affected.

### Patches

Path cleaning has accommodated for Git HTTP endpoints. Users should upgrade to 0.12.9 or the latest 0.13.0+dev.

### Workarounds

N/A

### References

https://huntr.dev/bounties/22f9c074-cf60-4c67-b5c4-72fdf312609d/

### For more information

If you have any questions or comments about this advisory, please post on #7002.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-6vcc-v9vw-g2x5
- https://nvd.nist.gov/vuln/detail/CVE-2022-1993
- https://github.com/gogs/gogs/issues/7002
- https://github.com/gogs/gogs/commit/9bf748b6c4c9a17d3aa77f6b9abcfae65451febf
- https://github.com/gogs/gogs
- https://huntr.dev/bounties/22f9c074-cf60-4c67-b5c4-72fdf312609d
