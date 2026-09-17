# [H] CVE-2025-65891

## Summary
Severity: High
Advisory: CVE-2025-65891
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2025-65891
Type: osv

## Details
A GPU device-ID validation flaw in OneFlow v0.9.0 allows attackers to trigger a Denial of Dervice (DoS) by invoking flow.cuda.get_device_properties() with an invalid or negative device index.

## References
- https://github.com/Daisy2ang
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65891.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65891
- https://github.com/Oneflow-Inc/oneflow/issues/10661
- https://github.com/Oneflow-Inc/oneflow
