# [H] CVE-2024-34246

## Summary
Severity: High
Advisory: CVE-2024-34246
Aliases: PYSEC-2024-307
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-06
Source: https://osv.dev/vulnerability/CVE-2024-34246
Type: osv

## Details
wasm3 v0.5.0 was discovered to contain an out-of-bound memory read which leads to segmentation fault via the function "main" in wasm3/platforms/app/main.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34246.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34246
- https://github.com/wasm3/wasm3/issues/484
