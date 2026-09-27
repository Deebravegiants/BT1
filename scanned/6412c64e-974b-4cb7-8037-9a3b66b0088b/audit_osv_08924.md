# [M] CVE-2016-6832

## Summary
Severity: Medium
Advisory: CVE-2016-6832
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-6832
Type: osv

## Details
Heap-based buffer overflow in the ff_audio_resample function in resample.c in libav before 11.4 allows remote attackers to cause a denial of service (crash) via vectors related to buffer resizing.

## References
- https://git.libav.org/?p=libav.git%3Ba=commit%3Bh=0ac8ff618c5e6d878c547a8877e714ed728950ce
- http://www.openwall.com/lists/oss-security/2016/08/18/1
- https://bugzilla.libav.org/show_bug.cgi?id=825
- http://www.openwall.com/lists/oss-security/2016/08/13/1
- https://blogs.gentoo.org/ago/2016/08/07/libav-heap-based-buffer-overflow-in-ff_audio_resample-resample-c/
