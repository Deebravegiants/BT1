# [M] CVE-2021-3479

## Summary
Severity: Medium
Advisory: CVE-2021-3479
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-03-31
Source: https://osv.dev/vulnerability/CVE-2021-3479
Type: osv

## Details
There's a flaw in OpenEXR's Scanline API functionality in versions before 3.0.0-beta. An attacker who is able to submit a crafted file to be processed by OpenEXR could trigger excessive consumption of memory, resulting in an impact to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2021/07/msg00001.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://security.gentoo.org/glsa/202107-27
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=25370
- https://bugzilla.redhat.com/show_bug.cgi?id=1939149
