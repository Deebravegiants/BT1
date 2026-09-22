# [M] CVE-2021-42780

## Summary
Severity: Medium
Advisory: CVE-2021-42780
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-04-18
Source: https://osv.dev/vulnerability/CVE-2021-42780
Type: osv

## Details
A use after return issue was found in Opensc before version 0.22.0 in insert_pin function that could potentially crash programs using the library.

## References
- https://lists.debian.org/debian-lts-announce/2023/06/msg00025.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00026.html
- https://security.gentoo.org/glsa/202209-03
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=28383
- https://bugzilla.redhat.com/show_bug.cgi?id=2016139
- https://github.com/OpenSC/OpenSC/commit/5df913b7
