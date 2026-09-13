# [H] Downloads Resources over HTTP in go-ipfs-dep

## Summary
Severity: High
Advisory: GHSA-g3xp-v2ff-x5c3
CVE: CVE-2016-10563
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-g3xp-v2ff-x5c3
Type: github-advisory

## Affected
- npm: `go-ipfs-dep` — affected >=0 <0.4.4

## Details
Affected versions of `go-ipfs-deps` insecurely download resources over HTTP. 

In scenarios where an attacker has a privileged network position, they can modify or read such resources at will. While the exact severity of impact for a vulnerability like this is highly variable and depends on the behavior of the package itself, it ranges from being able to read sensitive information all the way up to and including remote code execution.


## Recommendation

Update to version 0.4.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10563
- https://github.com/diasdavid/go-ipfs-dep/pull/12
- https://github.com/advisories/GHSA-g3xp-v2ff-x5c3
- https://www.npmjs.com/advisories/156
