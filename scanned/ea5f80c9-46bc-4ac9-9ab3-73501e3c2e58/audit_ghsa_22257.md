# [M] Logic error in Matrix SDK for Android

## Summary
Severity: Medium
Advisory: GHSA-jjmc-4p83-pp26
CVE: CVE-2021-40824
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jjmc-4p83-pp26
Type: github-advisory

## Affected
- Maven: `org.matrix.android:matrix-android-sdk2` — affected >=0 <1.2.2

## Details
A logic error in the room key sharing functionality of Element Android before 1.2.2 and matrix-android-sdk2 (aka Matrix SDK for Android) before 1.2.2 leads to a situation where identity verification is inadequate and thus a key-requesting device can be impersonated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40824
- https://github.com/matrix-org/matrix-android-sdk2/releases/tag/v1.2.2
- https://matrix.org/blog/2021/09/13/vulnerability-disclosure-key-sharing
