# [H] CVE-2026-50593

## Summary
Severity: High
Advisory: CVE-2026-50593
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-50593
Type: osv

## Details
Graphite before 1.3.15 has an integer underflow and resultant out-of-bounds write via Graphite actions, because slotat does not ensure that an offset is within the allowed slot-map range.

## References
- https://github.com/silnrsi/graphite/compare/1.3.14...1.3.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50593.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-50593
- https://github.com/silnrsi/graphite/commit/ad78c6b7319909e1540c1b134e115ced03417866
