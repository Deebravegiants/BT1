# [M] Authorization Bypass Through User-Controlled Key play-with-docker

## Summary
Severity: Medium
Advisory: GHSA-vq59-5x26-h639
CVE: CVE-2023-28109
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-17
Source: https://github.com/advisories/GHSA-vq59-5x26-h639
Type: github-advisory

## Affected
- Go: `github.com/play-with-docker/play-with-docker` — affected >=0

## Details
Impact
Give that CORS configuration was not correct, an attacker could use [play-with-docker.com](http://play-with-docker.com/) as an example, set origin header in http request as  [evil-play-with-docker.com](http://evil-play-with-docker.com/), it will be echo in response header, which successfully bypass the CORS policy and retrieves basic user information.

Patches
It has been fixed in lastest version, Please upgrade to latest version

Workarounds
No, users have to upgrade version.

## References
- https://github.com/play-with-docker/play-with-docker/security/advisories/GHSA-vq59-5x26-h639
- https://nvd.nist.gov/vuln/detail/CVE-2023-28109
- https://github.com/play-with-docker/play-with-docker/commit/ed82247c9ab7990ad76ec2bf1498c2b2830b6f1a
- https://github.com/play-with-docker/play-with-docker
