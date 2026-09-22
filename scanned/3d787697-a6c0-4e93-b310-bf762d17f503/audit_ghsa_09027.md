# [C] APScheduler's JSONSerializer and CBORSerializer are vulnerable to Remote Code Execution (RCE) via Insecure Deserialization

## Summary
Severity: Critical
Advisory: GHSA-9cfw-f3f9-7mm7
CVE: CVE-2026-31072
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-9cfw-f3f9-7mm7
Type: github-advisory

## Affected
- PyPI: `apscheduler` — affected >=4.0.0a1

## Details
The JSONSerializer and CBORSerializer in APScheduler (all versions including 3.10.x and 4.0.0a5) are vulnerable to Remote Code Execution (RCE) via Insecure Deserialization. The unmarshal_object function allows for arbitrary class instantiation and state injection by dynamically importing modules and calling __setstate__ on any class available in the Python environment. An attacker can exploit this by submitting a specially crafted JSON or CBOR payload to an application using these serializers

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31072
- https://gist.github.com/nedlir/11fb77f35a59cbba73392a086b02a9c6
- https://github.com/agronholm/apscheduler
