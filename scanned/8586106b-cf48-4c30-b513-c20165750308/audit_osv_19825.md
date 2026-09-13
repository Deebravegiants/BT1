# [M] CVE-2021-26260

## Summary
Severity: Medium
Advisory: CVE-2021-26260
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-06-08
Source: https://osv.dev/vulnerability/CVE-2021-26260
Type: osv

## Details
An integer overflow leading to a heap-buffer overflow was found in the DwaCompressor of OpenEXR in versions before 3.0.1. An attacker could use this flaw to crash an application compiled with OpenEXR. This is a different flaw from CVE-2021-23215.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BXFLD4ZAXKAIWO6ZPBCQEEDZB5IG676K/
- https://lists.debian.org/debian-lts-announce/2021/07/msg00001.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://www.debian.org/security/2022/dsa-5299
- https://bugzilla.redhat.com/show_bug.cgi?id=1947582
