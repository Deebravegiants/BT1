# [C] TimelockController vulnerability in OpenZeppelin Contracts

## Summary
Severity: Critical
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
CVE: CVE-2021-39167
CWE: Incorrect Privilege Assignment
Published: 2021-08-26
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-fg47-3c2x-m2wr
Type: github-advisory

## Details
### Impact

A vulnerability in `TimelockController` allowed an actor with the executor role to take immediate control of the timelock, by resetting the delay to 0 and escalating privileges, thus gaining unrestricted access to assets held in the contract. Instances with the executor role set to "open" allow anyone to use the executor role, thus leaving the timelock at risk of being taken over by an attacker.

### Patches

A fix is included in the following releases of `@openzeppelin/contracts` and `@openzeppelin/contracts-upgradeable`:
- 4.3.1
- 3.4.2
- 3.4.2-solc-0.7

Deployed instances of `TimelockController` should be replaced with a fixed version by migrating all assets, ownership, and roles.

### Workarounds

Revoke the executor role from accounts not strictly under the team's control. We recommend revoking all executors that are not also proposers. When applying this mitigation, ensure there is at least one proposer and executor remaining.

### References

[Post-mortem](https://forum.openzeppelin.com/t/timelockcontroller-vulnerability-postmortem/14958).

### Credits

The issue was identified by an anonymous white hat hacker through [Immunefi](https://immunefi.com/).

### For more information

If you have any questions or comments about this advisory, or need assistance executing the mitigation, email us at security@openzeppelin.com.
