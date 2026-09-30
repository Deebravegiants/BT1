# [M] CVE-2024-58131

## Summary
Severity: Medium
Advisory: CVE-2024-58131
CVSS: 4.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:L)
Published: 2025-04-06
Source: https://osv.dev/vulnerability/CVE-2024-58131
Type: osv

## Details
FISCO BCOS 3.11.0 has an issue with synchronization of the transaction pool that can, for example, be observed when a malicious node (that has modified the codebase to allow a large min_seal_time value) joins a blockchain network.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58131.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58131
- https://github.com/FISCO-BCOS/FISCO-BCOS/issues/4656
