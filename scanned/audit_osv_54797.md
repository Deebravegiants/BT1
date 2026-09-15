# [H] CVE-2024-43097

## Summary
Severity: High
Advisory: CVE-2024-43097
Aliases: A-350118416, ASB-A-350118416
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-03
Source: https://osv.dev/vulnerability/CVE-2024-43097
Type: osv

## Details
In resizeToAtLeast of SkRegion.cpp, there is a possible out of bounds write due to an integer overflow. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00006.html
- https://source.android.com/security/bulletin/2024-12-01
- https://android.googlesource.com/platform/external/skia/+/8d355fe1d0795fc30b84194b87563f75c6f8f2a7
