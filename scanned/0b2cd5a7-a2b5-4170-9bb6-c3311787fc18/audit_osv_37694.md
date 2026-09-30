# [H] CVE-2026-32775

## Summary
Severity: High
Advisory: CVE-2026-32775
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2026-32775
Type: osv

## Details
libexif through 0.6.25 has a flaw in decoding MakerNotes. If the exif_mnote_data_get_value function gets passed in a 0 size, the passed in-buffer would be overwritten due to an integer underflow.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32775.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-32775
- https://github.com/libexif/libexif/issues/247
- https://github.com/libexif/libexif/commit/7df372e9d31d7c993a22b913c813a5f7ec4f3692
