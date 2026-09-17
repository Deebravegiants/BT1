# [H] CVE-2021-41256

## Summary
Severity: High
Advisory: CVE-2021-41256
Aliases: GHSA-2q9v-q3cc-h9f3
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2021-11-30
Source: https://osv.dev/vulnerability/CVE-2021-41256
Type: osv

## Details
nextcloud news-android is an Android client for the Nextcloud news/feed reader app. In affected versions the Nextcloud News for Android app has a security issue by which a malicious application installed on the same device can send it an arbitrary Intent that gets reflected back, unintentionally giving read and write access to non-exported Content Providers in Nextcloud News for Android. Users should upgrade to version 0.9.9.63 or higher as soon as possible.

## References
- https://github.com/nextcloud/news-android/commit/05449cb666059af7de2302df9d5c02997a23df85
- https://github.com/nextcloud/news-android/security/advisories/GHSA-2q9v-q3cc-h9f3
- https://github.com/nextcloud/news-android/blob/master/security/GHSL-2021-1033_Nextcloud_News_for_Android.md
