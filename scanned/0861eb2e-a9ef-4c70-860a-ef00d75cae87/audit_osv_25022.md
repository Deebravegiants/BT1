# [M] CVE-2023-29570

## Summary
Severity: Medium
Advisory: CVE-2023-29570
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-29570
Type: osv

## Details
Cesanta MJS v2.20.0 was discovered to contain a SEGV vulnerability via mjs_ffi_cb_free at src/mjs_ffi.c. This vulnerability can lead to a Denial of Service (DoS).

## References
- https://github.com/z1r00/fuzz_vuln/blob/main/mjs/SEGV/mjs_fii2/readme.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29570.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29570
- https://github.com/cesanta/mjs/issues/240
