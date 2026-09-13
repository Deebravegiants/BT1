# [H] Incorrect Authorization in runc

## Summary
Severity: High
Advisory: GHSA-fgv8-vj5c-2ppq
CVE: CVE-2019-16884
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-22
Source: https://github.com/advisories/GHSA-fgv8-vj5c-2ppq
Type: github-advisory

## Affected
- Go: `github.com/opencontainers/runc` — affected >=0 <1.0.0-rc8.0.20190930145003-cad42f6e0932
- Go: `github.com/opencontainers/selinux` — affected >=0 <1.3.1-0.20190929122143-5215b1806f52

## Details
runc through 1.0.0-rc8, as used in Docker through 19.03.2-ce and other products, allows AppArmor restriction bypass because libcontainer/rootfs_linux.go incorrectly checks mount targets, and thus a malicious Docker image can mount over a /proc directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16884
- https://github.com/opencontainers/runc/issues/2128
- https://github.com/opencontainers/runc/pull/2129
- https://github.com/opencontainers/runc/pull/2130
- https://github.com/crosbymichael/runc/commit/78dce1cf1ec36bbe7fe6767bdb81f7cbf6d34d70
- https://github.com/opencontainers/runc/commit/cad42f6e0932db0ce08c3a3d9e89e6063ec283e4
- https://github.com/opencontainers/selinux/commit/03b517dc4fd57245b1cf506e8ba7b817b6d309da
- https://usn.ubuntu.com/4297-1
- https://security.netapp.com/advisory/ntap-20220221-0004
- https://security.gentoo.org/glsa/202003-21
- https://pkg.go.dev/vuln/GO-2021-0085
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SPK4JWP32BUIVDJ3YODZSOEVEW6BHQCF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DGK6IV5JGVDXHOXEKJOJWKOVNZLT6MYR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/62OQ2P7K5YDZ5BRCH2Q6DHUJIHQD3QCD
- https://lists.debian.org/debian-lts-announce/2023/02/msg00016.html
- https://github.com/opencontainers/runc
- https://access.redhat.com/errata/RHSA-2019:4269
- https://access.redhat.com/errata/RHSA-2019:4074
- https://access.redhat.com/errata/RHSA-2019:3940
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00073.html
