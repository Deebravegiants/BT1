# [M] tar-split memory exhaustion

## Summary
Severity: Medium
Advisory: GHSA-hqwh-8xv9-42hw
CVE: CVE-2017-14992
CWE: CWE-20, CWE-770
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-hqwh-8xv9-42hw
Type: github-advisory

## Affected
- Go: `github.com/vbatts/tar-split` — affected >=0 <0.10.2

## Details
Lack of content verification in Docker-CE (Also known as Moby) versions 1.12.6-0, 1.10.3, 17.03.0, 17.03.1, 17.03.2, 17.06.0, 17.06.1, 17.06.2, 17.09.0, and earlier allows a remote attacker to cause a Denial of Service via a crafted image layer payload, aka gzip bombing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14992
- https://github.com/moby/moby/issues/35075
- https://github.com/vbatts/tar-split/pull/42
- https://github.com/vbatts/tar-split
- https://github.com/vbatts/tar-split/releases/tag/v0.10.2
- https://web.archive.org/web/20171119174639/https://blog.cloudpassage.com/2017/10/13/discovering-docker-cve-2017-14992
