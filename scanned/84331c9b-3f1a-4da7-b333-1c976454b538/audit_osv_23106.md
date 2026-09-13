# [H] CVE-2022-43281

## Summary
Severity: High
Advisory: CVE-2022-43281
Aliases: PYSEC-2022-43187
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-10-28
Source: https://osv.dev/vulnerability/CVE-2022-43281
Type: osv

## Details
wasm-interp v1.0.29 was discovered to contain a heap overflow via the component std::vector<wabt::Type, std::allocator<wabt::Type>>::size() at /bits/stl_vector.h.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43281.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43281
- https://github.com/WebAssembly/wabt/issues/1981
