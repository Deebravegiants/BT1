# [H] Mapbox is vulnerable to Integer Overflow

## Summary
Severity: High
Advisory: GHSA-4696-g7jj-xg2h
CVE: CVE-2022-38216
CWE: CWE-190
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-17
Source: https://github.com/advisories/GHSA-4696-g7jj-xg2h
Type: github-advisory

## Affected
- Maven: `com.mapbox.mapboxsdk:mapbox-android-core` — affected >=0 <10.6.1

## Details
An integer overflow exists in Mapbox's closed source gl-native library prior to version 10.6.1, which is bundled with multiple Mapbox products including open source libraries. The overflow is caused by large image height and width values when creating a new Image and allows for out of bounds writes, potentially crashing the Mapbox process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38216
- https://github.com/mapbox/mapbox-maps-android
- https://github.com/mapbox/mapbox-maps-android/releases/tag/android-v10.6.1
