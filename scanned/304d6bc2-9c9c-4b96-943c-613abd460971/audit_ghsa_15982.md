# [C] NVIDIA Container Toolkit contains a Time-of-check Time-of-Use (TOCTOU) vulnerability

## Summary
Severity: Critical
Advisory: GHSA-mjjw-553x-87pq
CVE: CVE-2024-0132
CWE: CWE-367
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-mjjw-553x-87pq
Type: github-advisory

## Affected
- Go: `github.com/NVIDIA/nvidia-container-toolkit` — affected >=0 <1.16.2

## Details
NVIDIA Container Toolkit 1.16.1 or earlier contains a Time-of-check Time-of-Use (TOCTOU) vulnerability when used with default configuration where a specifically crafted container image may gain access to the host file system. This does not impact use cases where CDI is used. A successful exploit of this vulnerability may lead to code execution, denial of service, escalation of privileges, information disclosure, and data tampering.

## References
- https://github.com/NVIDIA/gpu-operator/security/advisories/GHSA-95rf-r6p4-44h7
- https://github.com/NVIDIA/libnvidia-container/security/advisories/GHSA-q2v4-jw5g-9xxj
- https://github.com/NVIDIA/nvidia-container-toolkit/security/advisories/GHSA-mjjw-553x-87pq
- https://nvd.nist.gov/vuln/detail/CVE-2024-0132
- https://github.com/NVIDIA/nvidia-container-toolkit
- https://nvidia.custhelp.com/app/answers/detail/a_id/5582
