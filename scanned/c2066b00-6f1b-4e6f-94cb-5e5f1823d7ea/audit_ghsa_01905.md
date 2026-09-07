# [H] Privilege Elevation in runc

## Summary
Severity: High
Advisory: GHSA-q3j5-32m5-58c2
CVE: CVE-2016-3697
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-q3j5-32m5-58c2
Type: github-advisory

## Affected
- Go: `github.com/opencontainers/runc` — affected >=0 <0.1.0

## Details
libcontainer/user/user.go in runC before 0.1.0, as used in Docker before 1.11.2, improperly treats a numeric UID as a potential username, which allows local users to gain privileges via a numeric username in the password file in a container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3697
- https://github.com/docker/docker/issues/21436
- https://github.com/opencontainers/runc/pull/708
- https://github.com/opencontainers/runc/commit/69af385de62ea68e2e608335cffbb0f4aa3db091
- https://github.com/opencontainers/runc
- https://github.com/opencontainers/runc/releases/tag/v0.1.0
- https://lists.opensuse.org/opensuse-updates/2016-05/msg00111.html
- https://pkg.go.dev/vuln/GO-2021-0070
- https://rhn.redhat.com/errata/RHSA-2016-1034.html
- https://rhn.redhat.com/errata/RHSA-2016-2634.html
- https://security.gentoo.org/glsa/201612-28
- http://rhn.redhat.com/errata/RHSA-2016-1034.html
- http://rhn.redhat.com/errata/RHSA-2016-2634.html
