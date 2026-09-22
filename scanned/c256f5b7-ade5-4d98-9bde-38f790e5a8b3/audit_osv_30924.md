# [C] HarfBuzz heap-buffer-overflow on hb_cairo_glyphs_from_buffer

## Summary
Severity: Critical
Advisory: CVE-2024-56732
Aliases: GHSA-qmp9-xqm5-jh6m
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56732
Type: osv

## Details
HarfBuzz is a text shaping engine. Starting with 8.5.0 through 10.0.1, there is a heap-based buffer overflow in the hb_cairo_glyphs_from_buffer function.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56732.json
- https://github.com/harfbuzz/harfbuzz/security/advisories/GHSA-qmp9-xqm5-jh6m
- https://nvd.nist.gov/vuln/detail/CVE-2024-56732
- https://github.com/harfbuzz/harfbuzz/commit/1767f99e2e2196c3fcae27db6d8b60098d3f6d26
