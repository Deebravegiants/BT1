# [M] OpenZeppelin Contracts initializer reentrancy may lead to double initialization

## Summary
Severity: Medium
Chain: Solidity
Component: @openzeppelin/contracts
CVE: CVE-2022-39384
CWE: Improper Initialization
Published: 2021-12-14
Source: https://github.com/advisories/GHSA-9c22-pwxw-p6hx
Type: github-advisory

## Details
### Impact

Initializer functions that are invoked separate from contract creation (the most prominent example being minimal proxies) may be reentered if they make an untrusted non-view external call.

Once an initializer has finished running it can never be re-executed. However, an exception put in place to support multiple inheritance made reentrancy possible in the scenario described above, breaking the expectation that there is a single execution.

Note that upgradeable proxies are commonly initialized together with contract creation, where reentrancy is not feasible, so the impact of this issue is believed to be minor.

### Patches

A fix is included in the version v4.4.1 of `@openzeppelin/contracts` and `@openzeppelin/contracts-upgradeable`.

### Workarounds

Avoid untrusted external calls during initialization.

### References
https://github.com/OpenZeppelin/openzeppelin-contracts/pull/3006

### Credits

This issue was identified and reported by @chaitinblockchain through [our bug bounty on Immunefi](https://immunefi.com/bounty/openzeppelin/).

### For more information

If you have any questions or comments about this advisory, or need assistance executing the mitigation, email us at security@openzeppelin.com.
