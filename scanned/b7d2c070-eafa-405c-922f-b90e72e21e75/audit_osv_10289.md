# [M] CVE-2017-14731

## Summary
Severity: Medium
Advisory: CVE-2017-14731
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-25
Source: https://osv.dev/vulnerability/CVE-2017-14731
Type: osv

## Details
ofx_proc_file in ofx_preproc.cpp in LibOFX 0.9.12 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted file, as demonstrated by an ofxdump call.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00038.html
- https://security.gentoo.org/glsa/201908-26
- https://github.com/libofx/libofx/issues/10
