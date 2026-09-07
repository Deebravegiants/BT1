# [M] Path Traversal in Docker

## Summary
Severity: Medium
Advisory: GHSA-vj3f-3286-r4pf
CVE: CVE-2014-9356
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-vj3f-3286-r4pf
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0 <1.3.3

## Details
Path traversal vulnerability in Docker before 1.3.3 allows remote attackers to write to arbitrary files and bypass a container protection mechanism via a full pathname in a symlink in an (1) image or (2) build in a Dockerfile.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9356
- https://access.redhat.com/security/cve/cve-2014-9356
- https://bugzilla.redhat.com/show_bug.cgi?id=1172761
- https://github.com/moby/moby
- https://groups.google.com/forum/#%21msg/docker-user/nFAz-B-n4Bw/0wr3wvLsnUwJ
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-9356
- http://www.securityfocus.com/archive/1/archive/1/534215/100/0/threaded
