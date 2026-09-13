# [H] NVIDIA Container Toolkit for all platforms contains a vulnerability in the update-ldcache hook

## Summary
Severity: High
Advisory: GHSA-67jc-hmvg-q4c7
CVE: CVE-2025-23267
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H (CVSS_V3)
Published: 2025-07-17
Source: https://github.com/advisories/GHSA-67jc-hmvg-q4c7
Type: github-advisory

## Affected
- Go: `github.com/NVIDIA/nvidia-container-toolkit` — affected >=0 <1.17.8
- Go: `github.com/NVIDIA/k8s-device-plugin` — affected >=0 <0.17.3
- Go: `github.com/NVIDIA/gpu-operator` — affected >=0 <25.3.2
- Go: `github.com/NVIDIA/mig-parted` — affected >=0 <0.12.2

## Details
NVIDIA Container Toolkit for all platforms contains a vulnerability in the update-ldcache hook, where an attacker could cause a link following by using a specially crafted container image. A successful exploit of this vulnerability might lead to data tampering and denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-23267
- https://github.com/NVIDIA/gpu-operator
- https://github.com/NVIDIA/k8s-device-plugin
- https://github.com/NVIDIA/mig-parted
- https://github.com/NVIDIA/nvidia-container-toolkit
- https://nvidia.custhelp.com/app/answers/detail/a_id/5659
- https://pkg.go.dev/vuln/GO-2025-3998
- http://www.openwall.com/lists/oss-security/2025/07/16/3
