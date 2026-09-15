# [M] CVE-2021-27815

## Summary
Severity: Medium
Advisory: CVE-2021-27815
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/CVE-2021-27815
Type: osv

## Details
NULL Pointer Deference in the exif command line tool, when printing out XML formatted EXIF data, in exif v0.6.22 and earlier allows attackers to cause a Denial of Service (DoS) by uploading a malicious JPEG file, causing the application to crash.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JSWAXZVNXYLV3E4R6YQTEGRGMGWEAR76/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QMC6OTXZRPCUD3LOSWO4ISR7CH7NJQDT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZQ3L45F7S7PQPG5HEHXOCGNOO64MJOS/
- https://security.gentoo.org/glsa/202210-28
- https://github.com/libexif/exif/commit/eb84b0e3c5f2a86013b6fcfb800d187896a648fa
- https://github.com/libexif/exif/commit/f6334d9d32437ef13dc902f0a88a2be0063d9d1c
- https://github.com/libexif/exif/issues/4
