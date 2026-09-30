# [H] CVE-2020-0181

## Summary
Severity: High
Advisory: CVE-2020-0181
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-11
Source: https://osv.dev/vulnerability/CVE-2020-0181
Type: osv

## Details
In exif_data_load_data_thumbnail of exif-data.c, there is a possible denial of service due to an integer overflow. This could lead to remote denial of service with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-10Android ID: A-145075076

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ELDZR6USD5PR34MRK2ZISLCYJ465FNKN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SVBD5JRUQPN4LQHTAAJHA3MR5M7YTAC7/
- https://security.gentoo.org/glsa/202011-19
- https://source.android.com/security/bulletin/pixel/2020-06-01
