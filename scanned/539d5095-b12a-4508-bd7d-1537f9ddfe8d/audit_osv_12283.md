# [M] CVE-2018-11224

## Summary
Severity: Medium
Advisory: CVE-2018-11224
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-17
Source: https://osv.dev/vulnerability/CVE-2018-11224
Type: osv

## Details
An issue was discovered in Libav 12.3. A read access violation in the in_table_init16 function in libavcodec/aacsbr.c allows remote attackers to cause a denial of service (application crash), as demonstrated by avconv.

## References
- https://bugzilla.libav.org/show_bug.cgi?id=1129
- https://docs.google.com/document/d/16_HC-FjFuBNMbaoR397z_3EwpDP6wb1DNWrfkD4qRDE/edit
