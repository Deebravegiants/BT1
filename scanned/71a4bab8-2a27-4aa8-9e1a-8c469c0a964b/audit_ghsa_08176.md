# [C] Microsoft Semantic Kernel InMemoryVectorStore filter functionality vulnerable to remote code execution

## Summary
Severity: Critical
Advisory: GHSA-xjw9-4gw8-4rqx
CVE: CVE-2026-26030
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-xjw9-4gw8-4rqx
Type: github-advisory

## Affected
- PyPI: `semantic-kernel` — affected >=0 <1.39.4

## Details
### Impact:
An RCE vulnerability has been identified in Microsoft Semantic Kernel Python SDK, specifically within the `InMemoryVectorStore` filter functionality.

### Patches:
The problem has been fixed in [python-1.39.4](https://github.com/microsoft/semantic-kernel/releases/tag/python-1.39.4). Users should upgrade this version or higher.

### Workarounds:
Avoid using `InMemoryVectorStore` for production scenarios.

### References:
[Release python-1.39.4 · microsoft/semantic-kernel · GitHub](https://github.com/microsoft/semantic-kernel/releases/tag/python-1.39.4)
[PR to block use of dangerous attribute names that must not be accessed in filter expressions](https://github.com/microsoft/semantic-kernel/pull/13505)

## References
- https://github.com/microsoft/semantic-kernel/security/advisories/GHSA-xjw9-4gw8-4rqx
- https://nvd.nist.gov/vuln/detail/CVE-2026-26030
- https://github.com/microsoft/semantic-kernel/pull/13505
- https://github.com/microsoft/semantic-kernel
- https://github.com/microsoft/semantic-kernel/releases/tag/python-1.39.4
- https://github.com/pypa/advisory-database/tree/main/vulns/semantic-kernel/PYSEC-2026-163.yaml
