# [H] Information Exposure in Docker Engine

## Summary
Severity: High
Advisory: GHSA-8fvr-5rqf-3wwh
CVE: CVE-2015-3630
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-8fvr-5rqf-3wwh
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=1.6.0 <1.6.1

## Details
Docker Engine before 1.6.1 uses weak permissions for (1) /proc/asound, (2) /proc/timer_stats, (3) /proc/latency_stats, and (4) /proc/fs, which allows local users to modify the host, obtain sensitive information, and perform protocol downgrade attacks via a crafted image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3630
- https://github.com/moby/moby/commit/545b440a80f676a506e5837678dd4c4f65e78660
- https://github.com/moby/moby
- https://groups.google.com/forum/#!searchin/docker-user/1.6.1/docker-user/47GZrihtr-4/nwgeOOFLexIJ
- https://groups.google.com/forum/#%21searchin/docker-user/1.6.1/docker-user/47GZrihtr-4/nwgeOOFLexIJ
- https://lists.opensuse.org/opensuse-updates/2015-05/msg00023.html
- https://packetstormsecurity.com/files/131835/Docker-Privilege-Escalation-Information-Disclosure.html
- https://seclists.org/fulldisclosure/2015/May/28
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2015-3630
- https://www.securityfocus.com/bid/74566
