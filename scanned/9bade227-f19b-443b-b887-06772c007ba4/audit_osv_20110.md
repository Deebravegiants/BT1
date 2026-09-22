# [M] CVE-2021-30501

## Summary
Severity: Medium
Advisory: CVE-2021-30501
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2021-30501
Type: osv

## Details
An assertion abort was found in upx MemBuffer::alloc() in mem.cpp, in version UPX 4.0.0. The flow allows attackers to cause a denial of service (abort) via a crafted file.

## References
- https://github.com/upx/upx/issues/486
- https://bugzilla.redhat.com/show_bug.cgi?id=1948696
- https://github.com/upx/upx/commit/28e761cd42211dfe0124b7a29b2f74730f453e46
- https://github.com/upx/upx/pull/487
