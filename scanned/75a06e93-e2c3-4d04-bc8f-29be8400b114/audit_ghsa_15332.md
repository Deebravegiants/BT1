# [M] s2n-tls's mTLS API ordering may skip client authentication

## Summary
Severity: Medium
Advisory: GHSA-857q-xmph-p2v5
CWE: CWE-287
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-09
Source: https://github.com/advisories/GHSA-857q-xmph-p2v5
Type: github-advisory

## Affected
- crates.io: `s2n-tls` — affected >=0 <0.3.0

## Details
### Impact

An API ordering issue in s2n-tls can cause client authentication to unexpectedly not be enabled on the server when it otherwise appears to be. Server applications are impacted if client authentication is enabled by calling s2n_connection_set_config() before calling s2n_connection_set_client_auth_type().

Applications are not impacted if these APIs are called in the opposite order, or if client authentication is enabled on the config with s2n_config_set_client_auth_type(). s2n-tls clients verifying server certificates are not impacted.

Impacted versions: < v1.5.0.


### Patches

The patch is included in v1.5.0 [1].


### Workarounds

Applications can workaround this issue by calling s2n_connection_set_config() after calling s2n_connection_set_client_auth_type(), or by enabling client authentication on the config with s2n_config_set_client_auth_type().

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our vulnerability reporting page [2] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

[1] https://github.com/aws/s2n-tls/releases/tag/v1.5.0

[2] https://aws.amazon.com/security/vulnerability-reporting

## References
- https://github.com/aws/s2n-tls/security/advisories/GHSA-857q-xmph-p2v5
- https://github.com/aws/s2n-tls/commit/e8ca8911c5b2f2361687dec1467c45cd54d00b3f
- https://github.com/aws/s2n-tls
