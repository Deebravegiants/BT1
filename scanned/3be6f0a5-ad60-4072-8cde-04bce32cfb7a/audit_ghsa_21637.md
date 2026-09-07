# [M] Symlink Attack in Libcontainer and Docker Engine

## Summary
Severity: Medium
Advisory: GHSA-g7v2-2qxx-wjrw
CVE: CVE-2015-3627
CWE: CWE-59
Ecosystem: Go
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-g7v2-2qxx-wjrw
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0 <1.6.1

## Details
Libcontainer and Docker Engine before 1.6.1 opens the file-descriptor passed to the pid-1 process before performing the chroot, which allows local users to gain privileges via a symlink attack in an image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3627
- https://github.com/docker/docker/commit/d5ebb60bddbabea0439213501f4f6ed494b23cba
- https://groups.google.com/forum/#!searchin/docker-user/1.6.1/docker-user/47GZrihtr-4/nwgeOOFLexIJ
- https://groups.google.com/forum/#%21searchin/docker-user/1.6.1/docker-user/47GZrihtr-4/nwgeOOFLexIJ
- https://lists.opensuse.org/opensuse-updates/2015-05/msg00023.html
- https://packetstormsecurity.com/files/131835/Docker-Privilege-Escalation-Information-Disclosure.html
- https://seclists.org/fulldisclosure/2015/May/28
