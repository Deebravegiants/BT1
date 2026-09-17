# [M] CVE-2017-15874

## Summary
Severity: Medium
Advisory: CVE-2017-15874
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-24
Source: https://osv.dev/vulnerability/CVE-2017-15874
Type: osv

## Details
archival/libarchive/decompress_unlzma.c in BusyBox 1.27.2 has an Integer Underflow that leads to a read access violation.

## References
- https://bugs.busybox.net/show_bug.cgi?id=10436
