# [M] CVE-2025-47183

## Summary
Severity: Medium
Advisory: CVE-2025-47183
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:H)
Published: 2025-08-07
Source: https://osv.dev/vulnerability/CVE-2025-47183
Type: osv

## Details
In GStreamer through 1.26.1, the isomp4 plugin's qtdemux_parse_tree function may read past the end of a heap buffer while parsing an MP4 file, leading to information disclosure.

## References
- https://gstreamer.freedesktop.org/security/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47183.json
- https://github.com/atredispartners/advisories/blob/master/2025/ATREDIS-2025-0003.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-47183
