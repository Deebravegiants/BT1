# [H] Romeo's invalid NetworkPolicy enables a malicious actor to pivot into another namespace 

## Summary
Severity: High
Advisory: GHSA-fgm3-q9r5-43v9
CVE: CVE-2026-32737
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-fgm3-q9r5-43v9
Type: github-advisory

## Affected
- Go: `github.com/ctfer-io/romeo/environment/deploy` — affected >=0 <0.2.1

## Details
### Impact

Due to a mis-written NetworkPolicy, a malicious actor can pivot from the "hardened" namespace to any Pod out of it.
This breaks the security-by-default property expected as part of the deployment program, leading to a potential lateral movement.

### Patch

Removing the `inter-ns` NetworkPolicy patches the vulnerability. If updates are not possible in production environments, we recommend to manually delete it and update as soon as possible.

### Workaround

Given your context, delete the failing network policy that should be prefixed by `inter-ns-` in the target namespace.

## References
- https://github.com/ctfer-io/romeo/security/advisories/GHSA-fgm3-q9r5-43v9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32737
- https://github.com/ctfer-io/romeo/commit/3bb5e9d9ce1199dfbb90fef8ad79ebdeb0bc5e78
- https://github.com/ctfer-io/romeo
