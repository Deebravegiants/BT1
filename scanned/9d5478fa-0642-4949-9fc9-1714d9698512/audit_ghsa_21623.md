# [H] Arbitrary File Write in Libcontainer

## Summary
Severity: High
Advisory: GHSA-g44j-7vp3-68cv
CVE: CVE-2015-3629
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-g44j-7vp3-68cv
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=1.6.0 <1.6.1

## Details
Libcontainer 1.6.0, as used in Docker Engine, allows local users to escape containerization ("mount namespace breakout") and write to arbitrary file on the host system via a symlink attack in an image when respawning a container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3629
- https://github.com/docker/docker/commit/d5ebb60bddbabea0439213501f4f6ed494b23cba
- https://groups.google.com/forum/#!searchin/docker-user/1.6.1/docker-user/47GZrihtr-4/nwgeOOFLexIJ
- https://groups.google.com/forum/#%21searchin/docker-user/1.6.1/docker-user/47GZrihtr-4/nwgeOOFLexIJ
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2015-3629
- http://lists.opensuse.org/opensuse-updates/2015-05/msg00023.html
- http://packetstormsecurity.com/files/131835/Docker-Privilege-Escalation-Information-Disclosure.html
- http://seclists.org/fulldisclosure/2015/May/28
- http://www.securityfocus.com/bid/74558
