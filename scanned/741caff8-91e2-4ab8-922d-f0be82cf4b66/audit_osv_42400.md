# [C] CVE-2026-68004

## Summary
Severity: Critical
Advisory: CVE-2026-68004
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-68004
Type: osv

## Details
An issue in OSSRS SRS (Simple Realtime Server) <v5.0.213 allows a remote attacker to execute arbitrary code via RTMP publish authorization, vhost-level security configuration (security.enabled), SrsSecurity::check(), trunk/src/app/srs_app_security.cpp, and SRS RTMP listener components

## References
- https://github.com/ossrs/srs/releases/tag/v5.0-r3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68004.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68004
- https://github.com/xuwu-xuwu/CVE-2026-68004
