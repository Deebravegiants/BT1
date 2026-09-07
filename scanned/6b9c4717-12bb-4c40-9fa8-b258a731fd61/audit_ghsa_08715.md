# [C] Ludwig framework is vulnerable to insecure deserialization in its model serving component

## Summary
Severity: Critical
Advisory: GHSA-xp5q-5q7g-q26r
CVE: CVE-2026-31238
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-xp5q-5q7g-q26r
Type: github-advisory

## Affected
- PyPI: `ludwig` — affected >=0

## Details
The Ludwig framework thru 0.10.4 is vulnerable to insecure deserialization (CWE-502) in its model serving component. When starting a model server with the ludwig serve command, the framework loads model weight files using torch.load() without enabling the security-restrictive weights_only=True parameter. This default behavior allows the deserialization of arbitrary Python objects via the pickle module. An attacker can exploit this by providing a maliciously crafted PyTorch model file, leading to arbitrary code execution on the system hosting the Ludwig model server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31238
- https://github.com/ludwig-ai/ludwig
- https://www.notion.so/CVE-2026-31238-35d1e1393188819ea77ee98ca85a2878
