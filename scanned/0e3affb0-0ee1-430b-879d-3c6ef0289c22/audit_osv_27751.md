# [H] CVE-2024-25431

## Summary
Severity: High
Advisory: CVE-2024-25431
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-25431
Type: osv

## Details
An issue in bytecodealliance wasm-micro-runtime before v.b3f728c and fixed in commit 06df58f allows a remote attacker to escalate privileges via a crafted file to the check_was_abi_compatibility function.

## References
- https://gist.github.com/haruki3hhh/bd228e6dcaf8c18140e1074964912b39
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25431.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25431
- https://github.com/bytecodealliance/wasm-micro-runtime/issues/3122
- https://github.com/bytecodealliance/wasm-micro-runtime/pull/3126
