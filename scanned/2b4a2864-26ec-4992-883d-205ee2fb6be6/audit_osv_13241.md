# [M] CVE-2018-18829

## Summary
Severity: Medium
Advisory: CVE-2018-18829
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-30
Source: https://osv.dev/vulnerability/CVE-2018-18829
Type: osv

## Details
There exists a NULL pointer dereference in ff_vc1_parse_frame_header_adv in vc1.c in Libav 12.3, which allows attackers to cause a denial-of-service through a crafted aac file.

## References
- https://bugzilla.libav.org/show_bug.cgi?id=1136
