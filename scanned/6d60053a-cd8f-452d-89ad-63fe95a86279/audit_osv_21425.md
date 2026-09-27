# [M] CVE-2021-42917

## Summary
Severity: Medium
Advisory: CVE-2021-42917
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-11-01
Source: https://osv.dev/vulnerability/CVE-2021-42917
Type: osv

## Details
Buffer overflow vulnerability in Kodi xbmc up to 19.0, allows attackers to cause a denial of service due to improper length of values passed to istream.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00009.html
- https://github.com/xbmc/xbmc/issues/20305
- https://github.com/fuzzard/xbmc/commit/80c8138c09598e88b4ddb6dbb279fa193bbb3237
- https://github.com/xbmc/xbmc/commit/48730b64494798705d46dfccc4029bd36d072df3
- https://github.com/xbmc/xbmc/pull/20306
