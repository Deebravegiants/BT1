# [M] Apache Knox allows impersonation of users

## Summary
Severity: Medium
Advisory: GHSA-g3fc-8jv4-qmmv
CVE: CVE-2017-5646
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-g3fc-8jv4-qmmv
Type: github-advisory

## Affected
- Maven: `org.apache.knox:gateway-provider-identity-assertion-common` — affected >=0.2.0 <0.12.0

## Details
For versions of Apache Knox from 0.2.0 to 0.11.0 - an authenticated user may use a specially crafted URL to impersonate another user while accessing WebHDFS through Apache Knox. This may result in escalated privileges and unauthorized data access. While this activity is audit logged and can be easily associated with the authenticated user, this is still a serious security issue. All users are recommended to upgrade to the Apache Knox 0.12.0 release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5646
- https://github.com/apache/knox/commit/998dcd257dc839c9651485760da4d614c16e2ca2
- https://github.com/apache/knox
- https://lists.apache.org/thread.html/rcd6bcbcc08840d4e4bea661efe9a5ef8f6126ebbbc5bc266701d8f48@%3Cdev.logging.apache.org%3E
- http://mail-archives.apache.org/mod_mbox/knox-user/201705.mbox/%3CCACRbFyjtT7QQGHUzTRdbJoySbJb7tt4BDk5-r-VRn0GB0Kgvag%40mail.gmail.com%3E
