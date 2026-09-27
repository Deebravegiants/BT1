# [C] UDS Identity Config has a client authentication bypass in `ClientIdAndKubernetesSecretAuthenticator`

## Summary
Severity: Critical
Advisory: CVE-2026-46389
Aliases: GHSA-8mg2-6588-r4hw
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-46389
Type: osv

## Details
UDS Identity Config builds the Keycloak configuration image (realm, plugins, theme, truststore, JARs) consumed by UDS Core's Identity deployment. In versions 0.11.0 through 0.26.0, a logic error in the `client-kubernetes-secret` Keycloak client authenticator (shipped by `uds-identity-config` and consumed by UDS Core) causes the submitted `client_secret` to be overwritten with the mounted Kubernetes secret before comparison. An attacker who can reach the Keycloak token endpoint and knows a `client_id` using this authenticator can authenticate as that client with any `client_secret` value and obtain OAuth2 tokens scoped to the client's service account. In the case of the `uds-operator` client this token can be used to registry/modify other clients. Version 0.26.1 patches the issue.

## References
- https://github.com/defenseunicorns/uds-identity-config/releases/tag/v0.26.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46389.json
- https://github.com/defenseunicorns/uds-identity-config/security/advisories/GHSA-8mg2-6588-r4hw
- https://nvd.nist.gov/vuln/detail/CVE-2026-46389
