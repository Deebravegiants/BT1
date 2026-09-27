# [M] CVE-2024-28577

## Summary
Severity: Medium
Advisory: CVE-2024-28577
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2024-28577
Type: osv

## Details
Null Pointer Dereference vulnerability in open source FreeImage v.3.19.0 [r1909] allows a local attacker to cause a denial of service (DoS) via the jpeg_read_exif_profile_raw() function when reading images in JPEG format.

## References
- https://github.com/Ruanxingzhi/vul-report/tree/master/freeimage-r1909
