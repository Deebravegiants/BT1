# [C] NVIDIA Container Toolkit for all platforms contains an Untrusted Search Path

## Summary
Severity: Critical
Advisory: GHSA-vmg3-7v43-9g23
CVE: CVE-2025-23266
CWE: CWE-426
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-17
Source: https://github.com/advisories/GHSA-vmg3-7v43-9g23
Type: github-advisory

## Affected
- Go: `github.com/NVIDIA/nvidia-container-toolkit` — affected >=0 <1.17.8
- Go: `github.com/NVIDIA/k8s-device-plugin` — affected >=0 <0.17.3
- Go: `github.com/NVIDIA/gpu-operator` — affected >=0 <25.3.2
- Go: `github.com/NVIDIA/mig-parted` — affected >=0 <0.12.2

## Details
NVIDIA Container Toolkit for all platforms contains a vulnerability in some hooks used to initialize the container, where an attacker could execute arbitrary code with elevated permissions. A successful exploit of this vulnerability might lead to escalation of privileges, data tampering, information disclosure, and denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-23266
- https://github.com/NVIDIA/gpu-operator
- https://github.com/NVIDIA/k8s-device-plugin
- https://github.com/NVIDIA/mig-parted
- https://github.com/NVIDIA/nvidia-container-toolkit
- https://kidbomb.github.io/posts/nvidia-container-escape-cve-2025-23266
- https://kidbomb.github.io/posts/nvidia-container-escape-cve-2025-23266-part-2
- https://news.ycombinator.com/item?id=44818412
- https://nvidia.custhelp.com/app/answers/detail/a_id/5659
- https://pkg.go.dev/vuln/GO-2025-3992
- https://www.wiz.io/blog/nvidia-ai-vulnerability-cve-2025-23266-nvidiascape
