# [M] zot logs secrets

## Summary
Severity: Medium
Advisory: GHSA-c37v-3c8w-crq8
CVE: CVE-2025-48374
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-05-22
Source: https://github.com/advisories/GHSA-c37v-3c8w-crq8
Type: github-advisory

## Affected
- Go: `zotregistry.dev/zot` — affected >=0 <1.4.4-0.20250522160828-8a99a3ed231f

## Details
### Summary
When using Keycloak as an oidc provider, the clientsecret gets printed into the container stdout logs for an example at container startup.

### Details
Container Image (15.04.2025): ghcr.io/project-zot/zot-linux-amd64:latest
Here is an example how the configuration can look which causes the above stated problem:

`    http:
      address: "0.0.0.0"
      port: 5000
      externalUrl: "https://zot.example.com"
      auth: {
        failDelay: 1,
        openid: {
          providers: {
            oidc: {
              name: "Keycloak",
              clientid: "zot-client-id",
              clientsecret: fsdfkmmiwljasdklfsjaskldjfkljewijrf234i52k3j45l,
              keypath: "",
              issuer: "https://keycloak.example.com/realms/example",
              scopes: ["openid"]
            }
          }
        }
      }
`

### PoC
Set up a blank new zot k8s deployment with the code snippet above.

### Impact
exposure of secrets, on configuring a oidc provider

## References
- https://github.com/project-zot/zot/security/advisories/GHSA-c37v-3c8w-crq8
- https://nvd.nist.gov/vuln/detail/CVE-2025-48374
- https://github.com/project-zot/zot/commit/8a99a3ed231fdcd8467e986182b4705342b6a15e
- https://github.com/project-zot/zot
- https://pkg.go.dev/vuln/GO-2025-3705
