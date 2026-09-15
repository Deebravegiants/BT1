# [C] Remote Command Execution in SOFARPC

## Summary
Severity: Critical
Advisory: GHSA-7q8p-9953-pxvr
CVE: CVE-2024-23636
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-23
Source: https://github.com/advisories/GHSA-7q8p-9953-pxvr
Type: github-advisory

## Affected
- Maven: `com.alipay.sofa:rpc-sofa-boot-starter` — affected >=0 <5.12.0

## Details
Impact
SOFARPC defaults to using the SOFA Hessian protocol to deserialize received data, while the SOFA Hessian protocol uses a blacklist mechanism to restrict deserialization of potentially dangerous classes for security protection. But there is a gadget chain that can bypass the SOFA Hessian blacklist protection mechanism, and this gadget chain only relies on JDK and does not rely on any third-party components.

Patches
Fixed this issue by adding a blacklist, users can upgrade to sofarpc version 5.12.0 to avoid this issue.

Workarounds
SOFARPC also provides a way to add additional blacklist. Users can add some class like -Drpc_serialize_blacklist_override=org.apache.xpath. to avoid this issue.

## References
- https://github.com/sofastack/sofa-rpc/security/advisories/GHSA-7q8p-9953-pxvr
- https://nvd.nist.gov/vuln/detail/CVE-2024-23636
- https://github.com/sofastack/sofa-rpc/commit/42d19b1b1d14a25aafd9ef7c219c04a19f90fc76
- https://github.com/sofastack/sofa-rpc/commit/d08e25824ae9feaf0876adba9acd2938f34759b1
- https://github.com/sofastack/sofa-rpc
