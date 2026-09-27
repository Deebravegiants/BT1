# [M] CVE-2025-23338

## Summary
Severity: Medium
Advisory: CVE-2025-23338
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-23338
Type: osv

## Details
NVIDIA CUDA Toolkit for all platforms contains a vulnerability in nvdisasm where a user may cause an out-of-bounds write by running nvdisasm on a malicious ELF file. A successful exploit of this vulnerability may lead to denial of service.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2169
- https://nvd.nist.gov/vuln/detail/CVE-2025-23338
- https://nvidia.custhelp.com/app/answers/detail/a_id/5661
- https://www.cve.org/CVERecord?id=CVE-2025-23338
