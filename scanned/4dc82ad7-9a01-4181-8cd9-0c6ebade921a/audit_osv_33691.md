# [M] hydra-node dangerously assumes L1 event finality and does not consider failed transactions

## Summary
Severity: Medium
Advisory: CVE-2025-48886
Aliases: GHSA-qr9f-mpgf-wp25
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2025-06-19
Source: https://osv.dev/vulnerability/CVE-2025-48886
Type: osv

## Details
Hydra is a layer-two scalability solution for Cardano. Prior to version 0.22.0, the process assumes L1 event finality and does not consider failed transactions. Currently, Cardano L1 is monitored for certain events which are necessary for state progression. At the moment, Hydra considers those events as finalized as soon as they are recognized by the node participants making such transactions the target of re-org attacks. The system does not currently consider the fact that failed transactions on the Cardano L1 can indeed appear in blocks because these transactions are so infrequent. This issue has been patched in version 0.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48886.json
- https://github.com/cardano-scaling/hydra/security/advisories/GHSA-qr9f-mpgf-wp25
- https://nvd.nist.gov/vuln/detail/CVE-2025-48886
- https://github.com/cardano-scaling/hydra/commit/2bc6a82ef6dbfa8b94e1c11d55253713065f605e
- https://github.com/cardano-scaling/hydra/commit/fb22d968964bf5d5b79227cc845d871147044ce7
