# [M] CVE-2019-14280

## Summary
Severity: Medium
Advisory: CVE-2019-14280
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-26
Source: https://osv.dev/vulnerability/CVE-2019-14280
Type: osv

## Details
In some circumstances, Craft 2 before 2.7.10 and 3 before 3.2.6 wasn't stripping EXIF data from user-uploaded images when it was configured to do so, potentially exposing personal/geolocation data to the public.

## References
- http://packetstormsecurity.com/files/154276/Craft-CMS-2.7.9-3.2.5-Information-Disclosure.html
- https://github.com/craftcms/cms/blob/develop-v2/CHANGELOG-v2.md#2710---2019-07-24
- https://github.com/craftcms/cms/blob/develop/CHANGELOG-v3.md#326---2019-07-23
