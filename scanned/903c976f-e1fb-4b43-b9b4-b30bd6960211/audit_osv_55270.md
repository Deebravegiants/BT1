# [H] CVE-2025-23308

## Summary
Severity: High
Advisory: CVE-2025-23308
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-23308
Type: osv

## Details
NVIDIA CUDA Toolkit for all platforms contains a vulnerability in nvdisasm where an attacker may cause a heap-based buffer overflow by getting the user to run nvdisasm on a malicious ELF file. A successful exploit of this vulnerability may lead to arbitrary code execution at the privilege level of the user running nvdisasm.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2204
- https://nvidia.custhelp.com/app/answers/detail/a_id/5661
- https://www.cve.org/CVERecord?id=CVE-2025-23308
- https://nvd.nist.gov/vuln/detail/CVE-2025-23308
