# [M] CVE-2025-47808

## Summary
Severity: Medium
Advisory: CVE-2025-47808
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-08-07
Source: https://osv.dev/vulnerability/CVE-2025-47808
Type: osv

## Details
In GStreamer through 1.26.1, the subparse plugin's tmplayer_parse_line function may dereference a NULL pointer while parsing a subtitle file, leading to a crash.

## References
- https://gstreamer.freedesktop.org/security/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47808.json
- https://github.com/atredispartners/advisories/blob/master/2025/ATREDIS-2025-0003.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-47808
