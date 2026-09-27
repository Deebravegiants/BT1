# [M] CVE-2021-20296

## Summary
Severity: Medium
Advisory: CVE-2021-20296
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-04-01
Source: https://osv.dev/vulnerability/CVE-2021-20296
Type: osv

## Details
A flaw was found in OpenEXR in versions before 3.0.0-beta. A crafted input file supplied by an attacker, that is processed by the Dwa decompression functionality of OpenEXR's IlmImf library, could cause a NULL pointer dereference. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2021/07/msg00001.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://security.gentoo.org/glsa/202107-27
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=24854
- https://bugzilla.redhat.com/show_bug.cgi?id=1939141
