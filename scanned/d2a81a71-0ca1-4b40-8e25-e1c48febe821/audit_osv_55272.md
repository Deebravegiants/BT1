# [H] CVE-2025-23339

## Summary
Severity: High
Advisory: CVE-2025-23339
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-23339
Type: osv

## Details
NVIDIA CUDA Toolkit for all platforms contains a vulnerability in cuobjdump where an attacker may cause a stack-based buffer overflow by getting the user to run cuobjdump on a malicious ELF file. A successful exploit of this vulnerability may lead to arbitrary code execution at the privilege level of the user running 
cuobjdump.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2155
- https://www.cve.org/CVERecord?id=CVE-2025-23339
- https://nvd.nist.gov/vuln/detail/CVE-2025-23339
- https://nvidia.custhelp.com/app/answers/detail/a_id/5661
