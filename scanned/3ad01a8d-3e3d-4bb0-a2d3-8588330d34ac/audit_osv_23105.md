# [H] CVE-2022-43280

## Summary
Severity: High
Advisory: CVE-2022-43280
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2022-10-28
Source: https://osv.dev/vulnerability/CVE-2022-43280
Type: osv

## Details
wasm-interp v1.0.29 was discovered to contain an out-of-bounds read via the component OnReturnCallExpr->GetReturnCallDropKeepCount.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43280.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43280
- https://github.com/WebAssembly/wabt/issues/1982
