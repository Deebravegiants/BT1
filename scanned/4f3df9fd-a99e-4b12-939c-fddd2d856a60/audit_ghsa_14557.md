# [H] Opencontainers runc Incorrect Authorization vulnerability

## Summary
Severity: High
Advisory: GHSA-vpvm-3wq2-2wvm
CVE: CVE-2023-27561
CWE: CWE-706
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-vpvm-3wq2-2wvm
Type: github-advisory

## Affected
- Go: `github.com/opencontainers/runc` — affected >=1.0.0-rc95 <1.1.5

## Details
runc 1.0.0-rc95 through 1.1.4 has Incorrect Access Control leading to Escalation of Privileges, related to `libcontainer/rootfs_linux.go`. To exploit this, an attacker must be able to spawn two containers with custom volume-mount configurations, and be able to run custom images. NOTE: this issue exists because of a CVE-2019-19921 regression.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27561
- https://github.com/opencontainers/runc/issues/2197#issuecomment-1437617334
- https://github.com/opencontainers/runc/issues/3751
- https://github.com/opencontainers/runc/pull/3785
- https://security.netapp.com/advisory/ntap-20241206-0004
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I6BF24VCZRFTYBTT3T7HDZUOTKOTNPLZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FYVE3GB4OG3BNT5DLQHYO4M5SXX33AQ5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FNB2UEDIIJCRQW4WJLZOPQJZXCVSXMLD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DHGVGGMKGZSJ7YO67TGGPFEHBYMS63VF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ANUGDBJ7NBUMSUFZUSKU3ZMQYZ2Z3STN
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I6BF24VCZRFTYBTT3T7HDZUOTKOTNPLZ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FYVE3GB4OG3BNT5DLQHYO4M5SXX33AQ5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FNB2UEDIIJCRQW4WJLZOPQJZXCVSXMLD
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DHGVGGMKGZSJ7YO67TGGPFEHBYMS63VF
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ANUGDBJ7NBUMSUFZUSKU3ZMQYZ2Z3STN
- https://lists.debian.org/debian-lts-announce/2023/03/msg00023.html
- https://github.com/opencontainers/runc/releases/tag/v1.1.5
- https://github.com/opencontainers/runc
- https://gist.github.com/LiveOverflow/c937820b688922eb127fb760ce06dab9
