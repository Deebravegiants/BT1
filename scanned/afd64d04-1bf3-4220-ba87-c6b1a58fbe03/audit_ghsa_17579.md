# [M] OpenBao allows cancellation of root rekey and recovery rekey operations without authentication

## Summary
Severity: Medium
Advisory: GHSA-prpj-rchp-9j5h
CVE: CVE-2025-52894
CWE: CWE-20, CWE-306
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-26
Source: https://github.com/advisories/GHSA-prpj-rchp-9j5h
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0.1.0
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20250625150133-fe75468822a2

## Details
### Impact

OpenBao and HashiCorp Vault allowed an attacker to perform unauthenticated, unaudited cancellation of root rekey and recovery rekey operations, effecting a denial of service.

### Patches

In OpenBao v2.2.2 and later, manually setting the configuration option `disable_unauthed_rekey_endpoints=true` allows an operator to deny these rarely-used endpoints on global listeners.

In a future OpenBao release [communicated on our website](https://openbao.org/docs/deprecation/), we will set this to `true` for all users and provide an authenticated alternative.

This vulnerability has been disclosed to HashiCorp; see their website for more information. 

### Workarounds

If an active proxy or load balancer sits in front of OpenBao, an operator can deny requests to these endpoints from unauthorized IP ranges.

### References

See the [deprecation notice](https://openbao.org/docs/deprecation/unauthed-rekey/).

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-prpj-rchp-9j5h
- https://nvd.nist.gov/vuln/detail/CVE-2025-52894
- https://github.com/openbao/openbao/commit/fe75468822a22a88318c6079425357a02ae5b77b
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/releases/tag/v2.3.1
- https://openbao.org/docs/deprecation
- https://openbao.org/docs/deprecation/unauthed-rekey
- https://pkg.go.dev/vuln/GO-2025-3783
