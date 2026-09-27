# [C] CVE-2020-0452

## Summary
Severity: Critical
Advisory: CVE-2020-0452
Aliases: A-159625731, ASB-A-159625731
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-10
Source: https://osv.dev/vulnerability/CVE-2020-0452
Type: osv

## Details
In exif_entry_get_value of exif-entry.c, there is a possible out of bounds write due to an integer overflow. This could lead to remote code execution if a third party app used this library to process remote image data with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-8.1 Android-9 Android-10 Android-11 Android-8.0Android ID: A-159625731

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ELDZR6USD5PR34MRK2ZISLCYJ465FNKN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SVBD5JRUQPN4LQHTAAJHA3MR5M7YTAC7/
- https://security.gentoo.org/glsa/202011-19
- https://source.android.com/security/bulletin/2020-11-01
