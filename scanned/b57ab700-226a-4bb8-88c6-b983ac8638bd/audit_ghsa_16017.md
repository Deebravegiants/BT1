# [M] NVIDIA Container Toolkit allows specially crafted container image to create empty files on the host file system

## Summary
Severity: Medium
Advisory: GHSA-f748-7hpg-88ch
CVE: CVE-2024-0133
CWE: CWE-367
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-f748-7hpg-88ch
Type: github-advisory

## Affected
- Go: `github.com/NVIDIA/nvidia-container-toolkit` — affected >=0 <1.16.2

## Details
NVIDIA Container Toolkit 1.16.1 or earlier contains a vulnerability in the default mode of operation allowing a specially crafted container image to create empty files on the host file system. This does not impact use cases where CDI is used. A successful exploit of this vulnerability may lead to data tampering.

## References
- https://github.com/NVIDIA/libnvidia-container/security/advisories/GHSA-xff4-h7r9-vrpf
- https://github.com/NVIDIA/nvidia-container-toolkit/security/advisories/GHSA-f748-7hpg-88ch
- https://nvd.nist.gov/vuln/detail/CVE-2024-0133
- https://advisory-inbox.githubapp.com/advisory_reviews/GHSA-wqq7-v22c-gpfp
- https://github.com/NVIDIA/nvidia-container-toolkit
- https://nvidia.custhelp.com/app/answers/detail/a_id/5582
