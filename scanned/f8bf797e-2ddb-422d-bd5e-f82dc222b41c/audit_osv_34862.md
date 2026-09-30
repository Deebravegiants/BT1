# [H] CVE-2025-65890

## Summary
Severity: High
Advisory: CVE-2025-65890
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2025-65890
Type: osv

## Details
A device-ID validation flaw in OneFlow v0.9.0 allows attackers to cause a Denial of Service (DoS) by calling flow.cuda.synchronize() with an invalid or out-of-range GPU device index.

## References
- https://github.com/Daisy2ang
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65890.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65890
- https://github.com/Oneflow-Inc/oneflow/issues/10662
- https://github.com/Oneflow-Inc/oneflow
