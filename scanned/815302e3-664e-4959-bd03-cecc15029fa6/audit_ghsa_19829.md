# [H] Ratify Azure authentication providers can leak authentication tokens to non-Azure container registries

## Summary
Severity: High
Advisory: GHSA-44f7-5fj5-h4px
CVE: CVE-2025-27403
CWE: CWE-287, CWE-497
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-44f7-5fj5-h4px
Type: github-advisory

## Affected
- Go: `github.com/ratify-project/ratify` — affected >=0 <1.2.3
- Go: `github.com/ratify-project/ratify` — affected >=1.3.0 <1.3.2
- Go: `github.com/deislabs/ratify` — affected >=0 <1.2.3

## Details
### Impact

In a Kubernetes environment, Ratify can be configured to authenticate to a private Azure Container Registry (ACR). The Azure workload identity and Azure managed identity authentication providers are configured in this setup. Users that configure a private ACR to be used with the Azure authentication providers may be impacted.
Both Azure authentication providers attempt to exchange an Entra ID (EID) token for an ACR refresh token. However, Ratify’s Azure authentication providers did not verify that the target registry is an ACR. This could have led to the EID token being presented to a non-ACR registry during token exchange. EID tokens with ACR access can potentially be extracted and abused if a user workload contains an image reference to a malicious registry.

### Patches

The Azure workload identity and Azure managed identity authentication providers are updated to add new validation prior to EID token exchange. Validation relies upon registry domain validation against a pre-configured list of well-known ACR endpoints. EID token exchange will be executed only if at least one of the configured well-known domain suffixes (wildcard support included) matches the registry domain of the image reference.

### Credits

The `ratify` project would like to thank Shiwei Zhang (@shizhMSFT) and Binbin Li (@binbin-li) for responsibly disclosing the issue and thank Binbin Li (@binbin-li) and Akash Singhal (@akashsinghal) for actively mitigating the issue.

## References
- https://github.com/ratify-project/ratify/security/advisories/GHSA-44f7-5fj5-h4px
- https://nvd.nist.gov/vuln/detail/CVE-2025-27403
- https://github.com/ratify-project/ratify/commit/0ec0c08490e3d672ae64b1a220c90d5484f1c93f
- https://github.com/ratify-project/ratify/commit/84c7c48fa76bb9a1c9583635d1e90bc25b1a546c
- https://github.com/ratify-project/ratify
- https://pkg.go.dev/vuln/GO-2025-3511
