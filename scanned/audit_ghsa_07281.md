# [H] Steeltoe's env sanitizer misses connection strings — leaks embedded DB passwords

## Summary
Severity: High
Advisory: GHSA-q62h-354g-5r85
CVE: CVE-2026-50200
CWE: CWE-200, CWE-319
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-q62h-354g-5r85
Type: github-advisory

## Affected
- NuGet: `Steeltoe.Management.Endpoint` — affected >=0 <4.2.0
- NuGet: `Steeltoe.Management.EndpointCore` — affected >=0 <3.4.0

## Details
### Summary

The `Sanitizer` component in the Environment actuator redacts configuration values by matching the configuration key name against a suffix list. The default list (`password`, `secret`, `key`, `token`, `.*credentials.*`, `vcap_services`) does not cover the standard .NET pattern `ConnectionStrings:<name>` or Steeltoe Connectors' `Steeltoe:Client:<type>:Default:ConnectionString`. There is no value-based scrubbing, so full connection string values including embedded `Password=` and `user:pass@host` segments are returned verbatim in `/actuator/env` responses.

### Impact

Any caller who can reach `/actuator/env` can receive connection strings containing plaintext credentials. Those credentials enable direct connection to the backing database, bypassing the application tier.

### Affected configuration

- Application configuration contains credentials in `ConnectionStrings:*` or `*:ConnectionString` keys.
- On standard deployments: `env` is added to `Management:Endpoints:Actuator:Exposure:Include`. This is not the default.
- On Cloud Foundry: the `/cloudfoundryapplication/env` path is accessible to any authenticated CF user with `read_basic_data` permissions (Space Auditor and above) regardless of the exposure configuration.

### Mitigations

If an immediate upgrade is not possible:

- On the standard path, remove `env` from the actuator exposure list.
- Add `.*connectionstring.*` to `KeysToSanitize` as a defense-in-depth measure for both paths.
- Require authorization on actuator endpoints.

## References
- https://github.com/SteeltoeOSS/security-advisories/security/advisories/GHSA-q62h-354g-5r85
- https://nvd.nist.gov/vuln/detail/CVE-2026-50200
- https://github.com/SteeltoeOSS/Steeltoe/commit/bef9f14b710232fca3fbe87e48fdd1b9e6b60d43
- https://github.com/SteeltoeOSS/Steeltoe/commit/e50cd31a429b191841120f0d38fa9dda8f751b0a
- https://github.com/SteeltoeOSS/Steeltoe
