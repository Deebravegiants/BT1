# [H] Hashicorp Vault vulnerable to Improper Check or Handling of Exceptional Conditions 

## Summary
Severity: High
Advisory: GHSA-2qmw-pvf7-4mw6
CVE: CVE-2024-6468
CWE: CWE-703
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-11
Source: https://github.com/advisories/GHSA-2qmw-pvf7-4mw6
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.10.0 <1.15.12
- Go: `github.com/hashicorp/vault` — affected >=1.16.0-rc1 <1.16.3
- Go: `github.com/hashicorp/vault` — affected >=1.17.0-rc1 <1.17.2

## Details
Vault and Vault Enterprise did not properly handle requests originating from unauthorized IP addresses when the TCP listener option, proxy_protocol_behavior, was set to deny_unauthorized. When receiving a request from a source IP address that was not listed in proxy_protocol_authorized_addrs, the Vault API server would shut down and no longer respond to any HTTP requests, potentially resulting in denial of service.

While this bug also affected versions of Vault up to 1.17.1 and 1.16.5, a separate regression in those release series did not allow Vault operators to configure the deny_unauthorized option, thus not allowing the conditions for the denial of service to occur.

Fixed in Vault and Vault Enterprise 1.17.2, 1.16.6, and 1.15.12

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6468
- https://discuss.hashicorp.com/t/hcsec-2024-14-vault-vulnerable-to-denial-of-service-when-setting-a-proxy-protocol-behavior/68518
- https://github.com/advisories/GHSA-2qmw-pvf7-4mw6
- https://github.com/hashicorp/vault
