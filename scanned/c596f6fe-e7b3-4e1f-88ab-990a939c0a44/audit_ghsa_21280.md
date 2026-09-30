# [H] FlyteAdmin's Default OAuth Authorization Server secret must be rotated

## Summary
Severity: High
Advisory: GHSA-67x4-qr35-qvrm
CVE: CVE-2022-39273
CWE: CWE-798
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-05
Source: https://github.com/advisories/GHSA-67x4-qr35-qvrm
Type: github-advisory

## Affected
- Go: `github.com/flyteorg/flyteadmin` — affected >=0 <1.1.44

## Details
### Impact
Users who enable the default [Flyte’s authorization server](https://docs.flyte.org/en/latest/deployment/cluster_config/auth_setup.html#oauth2-authorization-server) without changing the default clientid hashes will be exposed to the public internet.

In an effort to make enabling authentication easier for Flyte administrators, the default configuration for Flyte Admin allows access for Flyte Propeller even after turning on authentication via a hardcoded hashed password.  This password is also set on the default Flyte Propeller configmap in the various Flyte Helm charts.  Users who enable auth but do not override this setting in Flyte Admin’s configuration may unknowingly allow public traffic in by way of this default password with attackers effectively impersonating propeller.  This only applies to users who have not specified the ExternalAuthorizationServer setting.  Using an external auth server automatically turns off this default configuration is not susceptible to this vulnerability.

### Patches
1.1.44

### Workarounds
Users should manually set the staticClients in the selfAuthServer section of their configuration if they intend to rely on Admin’s internal auth server.  

### References
https://github.com/flyteorg/flyteadmin/pull/478
https://docs.flyte.org/en/latest/deployment/cluster_config/auth_setup.html#oauth2-authorization-server 

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Flyte](https://github.com/flyteorg/flyte/issues)
* Email us [here](mailto:admin@flyte.org)

## References
- https://github.com/flyteorg/flyteadmin/security/advisories/GHSA-67x4-qr35-qvrm
- https://nvd.nist.gov/vuln/detail/CVE-2022-39273
- https://github.com/flyteorg/flyteadmin/pull/478
- https://github.com/flyteorg/flyteadmin/commit/281172edf55fe6800959238fc128964ead6d9101
- https://docs.flyte.org/en/latest/deployment/cluster_config/auth_setup.html#oauth2-authorization-server
- https://github.com/flyteorg/flyteadmin
- https://pkg.go.dev/vuln/GO-2022-1043
