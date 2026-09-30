# [M] Directory Traversal in Docker

## Summary
Severity: Medium
Advisory: GHSA-qmmc-jppf-32wv
CVE: CVE-2014-9358
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-qmmc-jppf-32wv
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0 <1.3.2

## Details
Docker before 1.3.3 does not properly validate image IDs, which allows remote attackers to conduct path traversal attacks and spoof repositories via a crafted image in a (1) "docker load" operation or (2) "registry communications."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9358
- https://access.redhat.com/security/cve/cve-2014-9358
- https://groups.google.com/forum/#!msg/docker-user/nFAz-B-n4Bw/0wr3wvLsnUwJ
- https://groups.google.com/forum/#%21msg/docker-user/nFAz-B-n4Bw/0wr3wvLsnUwJ
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-9358
- http://www.securityfocus.com/archive/1/534215/100/0/threaded
