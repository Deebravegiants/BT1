# [H] Arbitrary Code Execution in Docker

## Summary
Severity: High
Advisory: GHSA-5qgp-p5jc-w2rm
CVE: CVE-2014-6407
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-5qgp-p5jc-w2rm
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0 <1.3.2

## Details
Docker before 1.3.2 allows remote attackers to write to arbitrary files and execute arbitrary code via a (1) symlink or (2) hard link attack in an image archive in a (a) pull or (b) load operation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-6407
- https://github.com/docker/docker/commit/3ac6394b8082d4700483d52fbfe54914be537d9e
- https://docs.docker.com/v1.3/release-notes
- https://lists.fedoraproject.org/pipermail/package-announce/2014-December/145154.html
- https://lists.opensuse.org/opensuse-security-announce/2014-12/msg00009.html
- https://secunia.com/advisories/60171
- https://secunia.com/advisories/60241
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-6407
- https://www.openwall.com/lists/oss-security/2014/11/24/5
