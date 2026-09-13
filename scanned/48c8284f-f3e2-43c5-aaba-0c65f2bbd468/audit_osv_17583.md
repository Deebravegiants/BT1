# [H] CVE-2020-17360

## Summary
Severity: High
Advisory: CVE-2020-17360
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-08-12
Source: https://osv.dev/vulnerability/CVE-2020-17360
Type: osv

## Details
An issue was discovered in ReadyTalk Avian 1.2.0. The vm::arrayCopy method defined in classpath-common.h contains multiple boundary checks that are performed to prevent out-of-bounds memory read/write. However, two of these boundary checks contain an integer overflow that leads to a bypass of these checks, and out-of-bounds read/write. NOTE: This vulnerability only affects products that are no longer supported by the maintainer

## References
- http://seclists.org/fulldisclosure/2020/Aug/8
- http://seclists.org/fulldisclosure/2020/Sep/11
- http://seclists.org/fulldisclosure/2020/Sep/13
- http://seclists.org/fulldisclosure/2020/Sep/14
- https://github.com/ReadyTalk/avian/issues
