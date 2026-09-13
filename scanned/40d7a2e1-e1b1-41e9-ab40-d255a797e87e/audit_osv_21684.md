# [M] CVE-2021-45293

## Summary
Severity: Medium
Advisory: CVE-2021-45293
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-12-21
Source: https://osv.dev/vulnerability/CVE-2021-45293
Type: osv

## Details
A Denial of Service vulnerability exists in Binaryen 103 due to an Invalid memory address dereference in wasm::WasmBinaryBuilder::visitLet.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UKGCHPS7UAIOOBGSXDJAUFE5CROTTF6J/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YCWLB4PWYQO55F7IGNC7KUYN2MFZE3JP/
- https://github.com/WebAssembly/binaryen/issues/4384
