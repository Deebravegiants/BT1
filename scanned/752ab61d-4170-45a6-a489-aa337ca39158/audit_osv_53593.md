# [M] CVE-2023-0193

## Summary
Severity: Medium
Advisory: CVE-2023-0193
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2023-03-10
Source: https://osv.dev/vulnerability/CVE-2023-0193
Type: osv

## Details
NVIDIA CUDA Toolkit SDK contains a vulnerability in cuobjdump, where a local user running the tool against a malicious binary may cause an out-of-bounds read, which may result in a limited denial of service and limited information disclosure.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5446
