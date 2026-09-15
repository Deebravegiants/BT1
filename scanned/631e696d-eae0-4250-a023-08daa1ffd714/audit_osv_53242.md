# [M] CVE-2022-34667

## Summary
Severity: Medium
Advisory: CVE-2022-34667
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2022-11-19
Source: https://osv.dev/vulnerability/CVE-2022-34667
Type: osv

## Details
NVIDIA CUDA Toolkit SDK contains a stack-based buffer overflow vulnerability in cuobjdump, where an unprivileged remote attacker could exploit this buffer overflow condition by persuading a local user to download a specially crafted corrupted file and execute cuobjdump against it locally, which may lead to a limited denial of service and some loss of data integrity for the local user.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5373
