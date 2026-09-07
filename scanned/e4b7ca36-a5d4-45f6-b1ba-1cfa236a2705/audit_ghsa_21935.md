# [M] Access Restriction Bypass in Docker

## Summary
Severity: Medium
Advisory: GHSA-44gg-pmqr-4669
CVE: CVE-2014-6408
CWE: CWE-285
Ecosystem: Go
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-44gg-pmqr-4669
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=1.3.0 <1.3.2

## Details
Docker 1.3.0 through 1.3.1 allows remote attackers to modify the default run profile of image containers and possibly bypass the container by applying unspecified security options to an image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-6408
- https://github.com/docker/docker/commit/c9379eb3fbbc484c056f5a5e49d8d0b755a29c45
- https://docs.docker.com/v1.3/release-notes
- https://lists.fedoraproject.org/pipermail/package-announce/2014-December/145154.html
- https://lists.opensuse.org/opensuse-security-announce/2014-12/msg00009.html
- https://secunia.com/advisories/60171
- https://secunia.com/advisories/60241
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-6408
- https://www.openwall.com/lists/oss-security/2014/11/24/5
