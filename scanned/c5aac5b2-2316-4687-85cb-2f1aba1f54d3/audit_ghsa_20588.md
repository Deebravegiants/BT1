# [H] android-gif-drawable vulerable to denial of service due to unrestricted comment length

## Summary
Severity: High
Advisory: GHSA-3mm4-w7v6-4rhv
CVE: CVE-2022-23435
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-20
Source: https://github.com/advisories/GHSA-3mm4-w7v6-4rhv
Type: github-advisory

## Affected
- Maven: `pl.droidsonroids.gif:android-gif-drawable` — affected >=0 <1.2.24

## Details
decoding.c in android-gif-drawable before 1.2.24 does not limit the maximum length of a comment, leading to denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23435
- https://github.com/koral--/android-gif-drawable/issues/792#issuecomment-1048850678
- https://github.com/koral--/android-gif-drawable/commit/9f0f0c89e6fa38548163771feeb4bde84b828887
- https://github.com/koral--/android-gif-drawable
- https://github.com/koral--/android-gif-drawable/compare/v1.2.23...v1.2.24
