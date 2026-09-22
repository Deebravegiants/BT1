# [M] CVE-2021-3933

## Summary
Severity: Medium
Advisory: CVE-2021-3933
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2021-3933
Type: osv

## Details
An integer overflow could occur when OpenEXR processes a crafted file on systems where size_t < 64 bits. This could cause an invalid bytesPerLine and maxBytesPerLine value, which could lead to problems with application stability or lead to other attack paths.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I2JSMJ7HLWFPYYV7IAQZD5ZUUUN7RWBN/
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://security.gentoo.org/glsa/202210-31
- https://www.debian.org/security/2022/dsa-5299
- https://bugzilla.redhat.com/show_bug.cgi?id=2019783
