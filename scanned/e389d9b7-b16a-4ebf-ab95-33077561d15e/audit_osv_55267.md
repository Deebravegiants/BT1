# [H] CVE-2025-23247

## Summary
Severity: High
Advisory: CVE-2025-23247
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/CVE-2025-23247
Type: osv

## Details
NVIDIA CUDA Toolkit for all platforms contains a vulnerability in the cuobjdump binary, where a failure to check the length of a buffer could allow a user to cause the tool to crash or execute arbitrary code by passing in a malformed ELF file. A successful exploit of this vulnerability might lead to arbitrary code execution.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5643
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2151
