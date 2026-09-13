# [M] CVE-2020-17361

## Summary
Severity: Medium
Advisory: CVE-2020-17361
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2020-08-12
Source: https://osv.dev/vulnerability/CVE-2020-17361
Type: osv

## Details
An issue was discovered in ReadyTalk Avian 1.2.0. The vm::arrayCopy method defined in classpath-common.h returns silently when a negative length is provided (instead of throwing an exception). This could result in data being lost during the copy, with varying consequences depending on the subsequent use of the destination buffer. NOTE: This vulnerability only affects products that are no longer supported by the maintainer

## References
- http://seclists.org/fulldisclosure/2020/Sep/11
- http://seclists.org/fulldisclosure/2020/Sep/13
- http://seclists.org/fulldisclosure/2020/Sep/14
- https://github.com/ReadyTalk/avian/issues
- http://seclists.org/fulldisclosure/2020/Aug/10
