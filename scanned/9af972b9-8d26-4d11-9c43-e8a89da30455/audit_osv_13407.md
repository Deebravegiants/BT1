# [M] CVE-2018-19758

## Summary
Severity: Medium
Advisory: CVE-2018-19758
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-30
Source: https://osv.dev/vulnerability/CVE-2018-19758
Type: osv

## Details
There is a heap-based buffer over-read at wav.c in wav_write_header in libsndfile 1.0.28 that will cause a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00030.html
- https://usn.ubuntu.com/4013-1/
- https://lists.debian.org/debian-lts-announce/2019/01/msg00008.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1643812
