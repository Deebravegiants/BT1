# [M] CVE-2020-3810

## Summary
Severity: Medium
Advisory: CVE-2020-3810
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-05-15
Source: https://osv.dev/vulnerability/CVE-2020-3810
Type: osv

## Details
Missing input validation in the ar/tar implementations of APT before version 2.1.2 could result in denial of service when processing specially crafted deb files.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U4PEH357MZM2SUGKETMEHMSGQS652QHH/
- https://lists.debian.org/debian-security-announce/2020/msg00089.html
- https://tracker.debian.org/news/1144109/accepted-apt-212-source-into-unstable/
- https://usn.ubuntu.com/4359-1/
- https://usn.ubuntu.com/4359-2/
- https://bugs.launchpad.net/bugs/1878177
- https://salsa.debian.org/apt-team/apt/-/commit/dceb1e49e4b8e4dadaf056be34088b415939cda6
- https://github.com/Debian/apt/issues/111
