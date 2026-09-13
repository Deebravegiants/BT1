# [H] CVE-2017-14040

## Summary
Severity: High
Advisory: CVE-2017-14040
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-14040
Type: osv

## Details
An invalid write access was discovered in bin/jp2/convert.c in OpenJPEG 2.2.0, triggering a crash in the tgatoimage function. The vulnerability may lead to remote denial of service or possibly unspecified other impact.

## References
- http://www.debian.org/security/2017/dsa-4013
- http://www.securityfocus.com/bid/100553
- https://blogs.gentoo.org/ago/2017/08/28/openjpeg-invalid-memory-write-in-tgatoimage-convert-c/
- https://github.com/uclouvain/openjpeg/commit/2cd30c2b06ce332dede81cccad8b334cde997281
- https://github.com/uclouvain/openjpeg/issues/995
