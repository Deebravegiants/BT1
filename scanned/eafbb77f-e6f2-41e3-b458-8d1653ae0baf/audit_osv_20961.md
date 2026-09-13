# [C] CVE-2021-39168

## Summary
Severity: Critical
Advisory: CVE-2021-39168
Aliases: GHSA-vrw4-w73r-6mm8
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/CVE-2021-39168
Type: osv

## Details
OpenZepplin is a library for smart contract development. In affected versions a vulnerability in TimelockController allowed an actor with the executor role to escalate privileges. Further details about the vulnerability will be disclosed at a later date. As a workaround revoke the executor role from accounts not strictly under the team's control. We recommend revoking all executors that are not also proposers. When applying this mitigation, ensure there is at least one proposer and executor remaining.

## References
- https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/security/advisories/GHSA-vrw4-w73r-6mm8
- https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/CHANGELOG.md#431
- https://github.com/OpenZeppelin/openzeppelin-contracts/commit/cec4f2ef57495d8b1742d62846da212515d99dd5
