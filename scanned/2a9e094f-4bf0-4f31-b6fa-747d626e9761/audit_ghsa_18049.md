# [C] ExecuTorch vulnerable to Heap-based Buffer Overflow

## Summary
Severity: Critical
Advisory: GHSA-xc7w-r669-48pf
CVE: CVE-2025-54951
CWE: CWE-122
Ecosystem: Maven, PyPI, SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-xc7w-r669-48pf
Type: github-advisory

## Affected
- PyPI: `executorch` — affected >=0 <0.7.0
- Maven: `org.pytorch:executorch-android` — affected >=0 <0.7.0
- SwiftURL: `github.com/pytorch/executorch` — affected >=0 <0.7.0

## Details
A group of related buffer overflow vulnerabilities in the loading of ExecuTorch models can cause the runtime to crash and potentially result in code execution or other undesirable effects. This issue affects ExecuTorch prior to commit cea9b23aa8ff78aff92829a466da97461cc7930c.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54951
- https://github.com/pytorch/executorch/commit/cea9b23aa8ff78aff92829a466da97461cc7930c
- https://github.com/pytorch/executorch
- https://www.facebook.com/security/advisories/cve-2025-54951
