# [H] CVE-2022-21821

## Summary
Severity: High
Advisory: CVE-2022-21821
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-29
Source: https://osv.dev/vulnerability/CVE-2022-21821
Type: osv

## Details
NVIDIA CUDA Toolkit SDK contains an integer overflow vulnerability in cuobjdump.To exploit this vulnerability, a remote attacker would require a local user to download a specially crafted, corrupted file and locally execute cuobjdump against the file. Such an attack may lead to remote code execution that causes complete denial of service and an impact on data confidentiality and integrity.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5334
