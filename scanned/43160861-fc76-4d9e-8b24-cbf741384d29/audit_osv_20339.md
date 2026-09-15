# [H] CVE-2021-32833

## Summary
Severity: High
Advisory: CVE-2021-32833
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2021-09-09
Source: https://osv.dev/vulnerability/CVE-2021-32833
Type: osv

## Details
Emby Server is a personal media server with apps on many devices. In Emby Server on Windows there is a set of arbitrary file read vulnerabilities. This vulnerability is known to exist in version 4.6.4.0 and may not be patched in later versions. Known vulnerable routes are /Videos/Id/hls/PlaylistId/SegmentId.SegmentContainer, /Images/Ratings/theme/name and /Images/MediaInfo/theme/name. For more details including proof of concept code, refer to the referenced GHSL-2021-051. This issue may lead to unauthorized access to the system especially when Emby Server is configured to be accessible from the Internet.

## References
- https://securitylab.github.com/advisories/GHSL-2021-051-emby/
