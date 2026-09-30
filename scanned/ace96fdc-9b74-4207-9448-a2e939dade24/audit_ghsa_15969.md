# [H] Hashicorp Vault vulnerable to denial of service through memory exhaustion

## Summary
Severity: High
Advisory: GHSA-g233-2p4r-3q7v
CVE: CVE-2024-8185
CWE: CWE-636
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-31
Source: https://github.com/advisories/GHSA-g233-2p4r-3q7v
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.2.0 <1.18.1
- Go: `github.com/openbao/openbao` — affected >=0 <2.0.3

## Details
Vault Community and Vault Enterprise (“Vault”) clusters using Vault’s Integrated Storage backend are vulnerable to a denial-of-service (DoS) attack through memory exhaustion through a Raft cluster join API endpoint. An attacker may send a large volume of requests to the endpoint which may cause Vault to consume excessive system memory resources, potentially leading to a crash of the underlying system and the Vault process itself.

This vulnerability, CVE-2024-8185, is fixed in Vault Community 1.18.1 and Vault Enterprise 1.18.1, 1.17.8, and 1.16.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8185
- https://github.com/hashicorp/vault/commit/195dfca433028887973f5bd82d173d91fe9dab4a
- https://discuss.hashicorp.com/t/hcsec-2024-26-vault-vulnerable-to-denial-of-service-through-memory-exhaustion-when-processing-raft-cluster-join-requests/71047
- https://github.com/hashicorp/vault
- https://openbao.org/docs/release-notes/2-0-0/#203
