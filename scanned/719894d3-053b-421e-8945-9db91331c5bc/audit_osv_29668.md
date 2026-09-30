# [M] OwnableTwoStep allows a pending owner to accept ownership after the original owner has renounced ownership in cairo-contracts

## Summary
Severity: Medium
Advisory: CVE-2024-45304
Aliases: GHSA-w2px-25pm-2cf9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-08-30
Source: https://osv.dev/vulnerability/CVE-2024-45304
Type: osv

## Details
Cairo-Contracts are OpenZeppelin Contracts written in Cairo for Starknet, a decentralized ZK Rollup. This vulnerability can lead to unauthorized ownership transfer, contrary to the original owner's intention of leaving the contract without an owner. It introduces a security risk where an unintended party (pending owner) can gain control of the contract after the original owner has renounced ownership. This could also be used by a malicious owner to simulate leaving a contract without an owner, to later regain ownership by previously having proposed himself as a pending owner. This issue has been addressed in release version 0.16.0. All users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/OpenZeppelin/cairo-contracts/releases/tag/v0.16.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45304.json
- https://github.com/OpenZeppelin/cairo-contracts/security/advisories/GHSA-w2px-25pm-2cf9
- https://nvd.nist.gov/vuln/detail/CVE-2024-45304
- https://github.com/OpenZeppelin/cairo-contracts/commit/ef87d7847980e0cf83f4b7f3ff23e6590fb643ec
