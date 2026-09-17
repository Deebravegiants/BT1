# [H] CVE-2020-0198

## Summary
Severity: High
Advisory: CVE-2020-0198
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-11
Source: https://osv.dev/vulnerability/CVE-2020-0198
Type: osv

## Details
In exif_data_load_data_content of exif-data.c, there is a possible UBSAN abort due to an integer overflow. This could lead to remote denial of service with no additional execution privileges needed. User interaction is needed for exploitation.Product: AndroidVersions: Android-10Android ID: A-146428941

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ELDZR6USD5PR34MRK2ZISLCYJ465FNKN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SVBD5JRUQPN4LQHTAAJHA3MR5M7YTAC7/
- https://security.gentoo.org/glsa/202011-19
- https://usn.ubuntu.com/4396-1/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00020.html
- https://source.android.com/security/bulletin/pixel/2020-06-01
