# [C] Moby Docker cp broken with debian containers

## Summary
Severity: Critical
Advisory: GHSA-v2cv-wwxq-qq97
CVE: CVE-2019-14271
CWE: CWE-665, CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v2cv-wwxq-qq97
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=19.03.0 <19.03.1

## Details
In Docker 19.03.x before 19.03.1 linked against the GNU C Library (aka glibc), code injection can occur when the nsswitch facility dynamically loads a library inside a chroot that contains the contents of the container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14271
- https://github.com/moby/moby/issues/39449
- https://github.com/moby/moby/pull/39612
- https://github.com/moby/moby/commit/11e48badcb67554b3d795241855028f28d244545
- https://github.com/moby/moby/commit/fa8dd90ceb7bcb9d554d27e0b9087ab83e54bd2b
- https://docs.docker.com/engine/release-notes
- https://github.com/moby/moby
- https://seclists.org/bugtraq/2019/Sep/21
- https://security.netapp.com/advisory/ntap-20190828-0003
- https://www.debian.org/security/2019/dsa-4521
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00084.html
