# [M] CVE-2019-3832

## Summary
Severity: Medium
Advisory: CVE-2019-3832
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2019-3832
Type: osv

## Details
It was discovered the fix for CVE-2018-19758 (libsndfile) was not complete and still allows a read beyond the limits of a buffer in wav_write_header() function in wav.c. A local attacker may use this flaw to make the application crash.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00030.html
- https://security.gentoo.org/glsa/202007-65
- https://usn.ubuntu.com/4013-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3832
- https://github.com/erikd/libsndfile/pull/460
- https://github.com/erikd/libsndfile/issues/456
