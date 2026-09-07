# [M] Steeltoe's sensitive actuators (heapdump/env) only require Restricted permission

## Summary
Severity: Medium
Advisory: GHSA-227r-jm2g-7cp4
CVE: CVE-2026-50201
CWE: CWE-269, CWE-285
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-227r-jm2g-7cp4
Type: github-advisory

## Affected
- NuGet: `Steeltoe.Management.Endpoint` — affected >=0 <4.2.0
- NuGet: `Steeltoe.Management.EndpointBase` — affected >=0 <3.4.0

## Details
### Summary

All Steeltoe actuator endpoints default to `EndpointPermissions.Restricted`, which is mapped to Cloud Foundry's `read_basic_data` permission (granted to Space Auditors and similar low-trust roles). Sensitive actuators including heap dump, environment, and thread dump do not raise this to `EndpointPermissions.Full`, so CF's `read_sensitive_data` permission flag is not enforced for those endpoints. Spring Boot's equivalent Cloud Foundry integration gates these endpoints with `read_sensitive_data` by default.

### Impact

Any CF user holding Space Auditor, Space Manager, or Org Auditor role can access the heap dump, environment, and thread dump actuators for any Steeltoe application in their space. A heap dump contains all in-memory data including database passwords, bearer tokens, and VCAP_SERVICES credentials. CF's `read_sensitive_data` permission, which is specifically designed to gate this access, has no effect.

### Affected configuration

- Application is deployed on Cloud Foundry with CF actuator and security middleware active (added automatically by `AddAllActuators()` when a CF environment is detected).
- The attacker holds a CF role that grants `read_basic_data`: Space Auditor, Space Manager, or Org Auditor.

### Mitigations

If an immediate upgrade is not possible:

- Explicitly set `RequiredPermissions = EndpointPermissions.Full` in the options for `HeapDumpEndpointOptions`, `EnvironmentEndpointOptions`, and `ThreadDumpEndpointOptions`.
- If heap dump, thread dump, or environment are not needed in production, register only the required actuators individually instead of using `AddAllActuators()`.

## References
- https://github.com/SteeltoeOSS/security-advisories/security/advisories/GHSA-227r-jm2g-7cp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-50201
- https://github.com/SteeltoeOSS/Steeltoe/commit/b39defa4db5f44f8696c456866b3a5b900d8d96b
- https://github.com/SteeltoeOSS/Steeltoe/commit/da6c604decd992f61aeef763f5814102dcb088c7
- https://github.com/SteeltoeOSS/security-advisories
