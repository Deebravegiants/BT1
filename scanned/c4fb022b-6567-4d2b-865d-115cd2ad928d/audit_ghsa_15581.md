# [H] SOFA Hessian Remote Command Execution (RCE) Vulnerability

## Summary
Severity: High
Advisory: GHSA-c459-2m73-67hj
CVE: CVE-2024-46983
CWE: CWE-502, CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-19
Source: https://github.com/advisories/GHSA-c459-2m73-67hj
Type: github-advisory

## Affected
- Maven: `com.alipay.sofa:hessian` — affected >=0 <3.5.5

## Details
### Impact
SOFA Hessian protocol uses a blacklist mechanism to restrict deserialization of potentially dangerous classes for security protection. But there is a gadget chain that can bypass the SOFA Hessian blacklist protection mechanism, and this gadget chain only relies on JDK and does not rely on any third-party components.

### Patches
Fixed this issue by update blacklist, users can upgrade to sofahessian version 3.5.5 to avoid this issue.

### Workarounds
You can maintain a blacklist yourself in this directory `external/serialize.blacklist`.

## References
- https://github.com/sofastack/sofa-hessian/security/advisories/GHSA-c459-2m73-67hj
- https://nvd.nist.gov/vuln/detail/CVE-2024-46983
- https://github.com/sofastack/sofa-hessian/commit/764ef4b216aee6aeb4b111aec8947a4e8b53bb87
- https://github.com/sofastack/sofa-hessian
