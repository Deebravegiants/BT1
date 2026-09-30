# [C] CVE-2025-23304

## Summary
Severity: Critical
Advisory: CVE-2025-23304
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-13
Source: https://osv.dev/vulnerability/CVE-2025-23304
Type: osv

## Details
NVIDIA NeMo library for all platforms contains a vulnerability in the model loading component, where an attacker could cause code injection by loading .nemo files with maliciously crafted metadata. A successful exploit of this vulnerability may lead to remote code execution and data tampering.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-23304
- https://nvidia.custhelp.com/app/answers/detail/a_id/5686
- https://www.cve.org/CVERecord?id=CVE-2025-23304
