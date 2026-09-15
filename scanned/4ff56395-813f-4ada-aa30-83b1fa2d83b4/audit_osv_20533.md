# [M] CVE-2021-3475

## Summary
Severity: Medium
Advisory: CVE-2021-3475
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-03-30
Source: https://osv.dev/vulnerability/CVE-2021-3475
Type: osv

## Details
There is a flaw in OpenEXR in versions before 3.0.0-beta. An attacker who can submit a crafted file to be processed by OpenEXR could cause an integer overflow, potentially leading to problems with application availability.

## References
- https://lists.debian.org/debian-lts-announce/2021/07/msg00001.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://security.gentoo.org/glsa/202107-27
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=25297
- https://bugzilla.redhat.com/show_bug.cgi?id=1939144
