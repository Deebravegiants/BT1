# [M] Governor proposal creation may be blocked by frontrunning

## Summary
Severity: Medium
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
CVE: CVE-2023-34234
Published: 2023-06-07
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-5h3x-9wvq-w4m2
Type: github-advisory

## Details
### Impact

By frontrunning the creation of a proposal, an attacker can become the proposer and gain the ability to cancel it. The attacker can do this repeatedly to try to prevent a proposal from being proposed at all.

This impacts the `Governor` contract in v4.9.0 only, and the `GovernorCompatibilityBravo` contract since v4.3.0.

### Patches

The problem has been patched in 4.9.1 by introducing opt-in frontrunning protection.

### Workarounds

Submit the proposal creation transaction to an endpoint with frontrunning protection.

### Credit

Reported by Lior Abadi and Joaquin Pereyra from Coinspect.

### References

https://www.coinspect.com/openzeppelin-governor-dos/
