# [C] DeepJavaLibrary API absolute path traversal

## Summary
Severity: Critical
Advisory: GHSA-w877-jfw7-46rj
CVE: CVE-2024-37902
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-17
Source: https://github.com/advisories/GHSA-w877-jfw7-46rj
Type: github-advisory

## Affected
- Maven: `ai.djl:api` — affected >=0.1.0 <0.28.0

## Details
## Summary

DeepJavaLibrary(DJL) versions 0.1.0 through 0.27.0 do not prevent absolute path archived artifacts from inserting archived files directly into the system, overwriting system files. This is fixed in DJL 0.28.0 and patched in DJL Large Model Inference containers 0.27.0.

**Impacted versions: 0.1.0 through 0.27.0**

## Patches

Patched Deep Learning Containers:
[v1.1-djl-0.27.0-inf-cpu-full](https://github.com/aws/deep-learning-containers/releases/tag/v1.1-djl-0.27.0-inf-cpu-full)
[v1.4-djl-0.27.0-inf-ds-0.12.6](https://github.com/aws/deep-learning-containers/releases/tag/v1.4-djl-0.27.0-inf-ds-0.12.6)
[v1.4-djl-0.27.0-inf-trt-0.8.0](https://github.com/aws/deep-learning-containers/releases/tag/v1.4-djl-0.27.0-inf-trt-0.8.0)
[v1.3-djl-0.27.0-inf-neuronx-sdk2.18.1](https://github.com/aws/deep-learning-containers/releases/tag/v1.3-djl-0.27.0-inf-neuronx-sdk2.18.1)

Patched Library:
[v0.28.0](https://github.com/deepjavalibrary/djl/releases/tag/v0.28.0)

## References
- https://github.com/deepjavalibrary/djl/security/advisories/GHSA-w877-jfw7-46rj
- https://nvd.nist.gov/vuln/detail/CVE-2024-37902
- https://github.com/aws/deep-learning-containers/releases/tag/v1.1-djl-0.27.0-inf-cpu-full
- https://github.com/aws/deep-learning-containers/releases/tag/v1.3-djl-0.27.0-inf-neuronx-sdk2.18.1
- https://github.com/aws/deep-learning-containers/releases/tag/v1.4-djl-0.27.0-inf-ds-0.12.6
- https://github.com/aws/deep-learning-containers/releases/tag/v1.4-djl-0.27.0-inf-trt-0.8.0
- https://github.com/deepjavalibrary/djl
- https://github.com/deepjavalibrary/djl/releases/tag/v0.28.0
