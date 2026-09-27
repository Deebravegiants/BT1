# [M] CVE-2015-9274

## Summary
Severity: Medium
Advisory: CVE-2015-9274
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-15
Source: https://osv.dev/vulnerability/CVE-2015-9274
Type: osv

## Details
HarfBuzz before 1.0.4 allows remote attackers to cause a denial of service (invalid read of two bytes and application crash) because of GPOS and GSUB table mishandling, related to hb-ot-layout-gpos-table.hh, hb-ot-layout-gsub-table.hh, and hb-ot-layout-gsubgpos-private.hh.

## References
- https://github.com/harfbuzz/harfbuzz/commit/c917965b9e6fe2b21ed6c51559673288fa3af4b7
- https://github.com/harfbuzz/harfbuzz/commit/c917965b9e6fe2b21ed6c51559673288fa3af4b7
