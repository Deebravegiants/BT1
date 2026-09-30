# [M] CVE-2018-17236

## Summary
Severity: Medium
Advisory: CVE-2018-17236
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-20
Source: https://osv.dev/vulnerability/CVE-2018-17236
Type: osv

## Details
The function MP4Free() in mp4property.cpp in libmp4v2 2.1.0 internally calls free() on a invalid pointer, raising a SIGABRT signal.

## References
- https://github.com/enzo1982/mp4v2/releases/tag/v2.1.0
- https://bugzilla.redhat.com/show_bug.cgi?id=1629453
