# [H] CVE-2024-34252

## Summary
Severity: High
Advisory: CVE-2024-34252
Aliases: GHSA-hh39-vjv8-j337, PYSEC-2024-309
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-06
Source: https://osv.dev/vulnerability/CVE-2024-34252
Type: osv

## Details
wasm3 v0.5.0 was discovered to contain a global buffer overflow which leads to segmentation fault via the function "PreserveRegisterIfOccupied" in wasm3/source/m3_compile.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34252.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34252
- https://github.com/wasm3/wasm3/issues/483
