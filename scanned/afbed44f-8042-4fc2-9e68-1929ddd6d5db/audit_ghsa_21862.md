# [M] Arbitrary File Override in Docker Engine

## Summary
Severity: Medium
Advisory: GHSA-v4h8-794j-g8mm
CVE: CVE-2015-3631
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-v4h8-794j-g8mm
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0 <1.6.1

## Details
Docker Engine before 1.6.1 allows local users to set arbitrary Linux Security Modules (LSM) and docker_t policies via an image that allows volumes to override files in /proc.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3631
- https://github.com/moby/moby
- https://github.com/moby/moby/compare/769acfec2928c47a35da5357d854145b1036448d...b6a9dc399be31c531e3753104e10d74760ed75a2
- https://groups.google.com/forum/#!searchin/docker-user/1.6.1/docker-user/47GZrihtr-4/nwgeOOFLexIJ
- https://groups.google.com/forum/#%21searchin/docker-user/1.6.1/docker-user/47GZrihtr-4/nwgeOOFLexIJ
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2015-3631
- http://lists.opensuse.org/opensuse-updates/2015-05/msg00023.html
- http://packetstormsecurity.com/files/131835/Docker-Privilege-Escalation-Information-Disclosure.html
- http://seclists.org/fulldisclosure/2015/May/28
