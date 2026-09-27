# [M] CVE-2020-25665

## Summary
Severity: Medium
Advisory: CVE-2020-25665
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-08
Source: https://osv.dev/vulnerability/CVE-2020-25665
Type: osv

## Details
The PALM image coder at coders/palm.c makes an improper call to AcquireQuantumMemory() in routine WritePALMImage() because it needs to be offset by 256. This can cause a out-of-bounds read later on in the routine. The patch adds 256 to bytes_per_row in the call to AcquireQuantumMemory(). This could cause impact to reliability. This flaw affects ImageMagick versions prior to 7.0.8-68.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00010.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1891606
