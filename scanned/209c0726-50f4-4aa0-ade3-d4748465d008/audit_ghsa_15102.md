# [M] Path Traversal in Moby builder

## Summary
Severity: Medium
Advisory: GHSA-6hwg-w5jg-9c6x
CVE: CVE-2020-27534
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-6hwg-w5jg-9c6x
Type: github-advisory

## Affected
- Go: `github.com/moby/moby` — affected >=0 <19.03.9
- Go: `github.com/docker/docker` — affected >=0 <19.03.9

## Details
util/binfmt_misc/check.go in Builder in Docker Engine before 19.03.9 calls os.OpenFile with a potentially unsafe qemu-check temporary pathname, constructed with an empty first argument in an ioutil.TempDir call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27534
- https://github.com/moby/buildkit/pull/1462
- https://github.com/moby/moby/pull/40877
- https://bugzilla.redhat.com/show_bug.cgi?id=1921154
- http://web.archive.org/web/20200530054359/https://docs.docker.com/engine/release-notes
