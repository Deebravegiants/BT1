# [M] CVE-2021-37600

## Summary
Severity: Medium
Advisory: CVE-2021-37600
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/CVE-2021-37600
Type: osv

## Details
An integer overflow in util-linux through 2.37.1 can potentially cause a buffer overflow if an attacker were able to use system resources in a way that leads to a large number in the /proc/sysvipc/sem file. NOTE: this is unexploitable in GNU C Library environments, and possibly in all realistic environments.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00005.html
- https://security.gentoo.org/glsa/202401-08
- https://security.netapp.com/advisory/ntap-20210902-0002/
- https://github.com/karelzak/util-linux/issues/1395
- https://github.com/karelzak/util-linux/commit/1c9143d0c1f979c3daf10e1c37b5b1e916c22a1c
