# [C] CVE-2021-3420

## Summary
Severity: Critical
Advisory: CVE-2021-3420
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-05
Source: https://osv.dev/vulnerability/CVE-2021-3420
Type: osv

## Details
A flaw was found in newlib in versions prior to 4.0.0. Improper overflow validation in the memory allocation functions mEMALIGn, pvALLOc, nano_memalign, nano_valloc, nano_pvalloc could case an integer overflow, leading to an allocation of a small buffer and then to a heap-based buffer overflow.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AEBF6YHWFNCBW5A2ENSQ3Z56ELF4MTRE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AMK54N6UOPBFFX2YT32TWSAEFTHGSKAA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LSQZEUANAWBBAOC4TF5PTPJVLMUR7SFD/
- https://bugzilla.redhat.com/show_bug.cgi?id=1934088
