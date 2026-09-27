# [H] Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-997c-fj8j-rq5h
CVE: CVE-2014-9357
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-997c-fj8j-rq5h
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0 <1.3.3

## Details
Docker 1.3.2 allows remote attackers to execute arbitrary code with root privileges via a crafted (1) image or (2) build in a Dockerfile in an LZMA (.xz) archive, related to the chroot for archive extraction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9357
- https://github.com/docker/docker/compare/aef842e7dfb534aba22c3c911de525ce9ac12b72...313a1b7620910e47d888f8b0a6a5eb06ad9c1ff2
- https://github.com/moby/moby/blob/master/CHANGELOG.md#133-2014-12-11
- https://groups.google.com/forum/#!msg/docker-user/nFAz-B-n4Bw/0wr3wvLsnUwJ
- https://groups.google.com/forum/#%21msg/docker-user/nFAz-B-n4Bw/0wr3wvLsnUwJ
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-9357
- http://www.securityfocus.com/archive/1/534215/100/0/threaded
