# [M] Evmos vulnerable to unauthorized account creation with vesting module

## Summary
Severity: Medium
Chain: github.com/evmos/evmos/v13/x/vesting
Component: github.com/evmos/evmos/v13/x/vesting, github.com/evmos/evmos/v13
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-m99c-q26r-m7m7
Type: github-advisory

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Using the vesting module, a malicious attacker can create a new vesting account at a given
address, before a contract is created on that address.

Addresses of smart contracts deployed to the EVM are deterministic. Therefore, it would be possible for an attacker to front-run a contract creation and create a vesting account at that address. 
When an address has been initialized without any contract code deployed to it, it will not be possible to upload any afterwards. In the described attack, this would mean that a malicious actor could prevent smart contracts from being deployed correctly.

In order to remediate this, an alternative user flow is being implemented for the vesting module:
- only the account receiving the vesting funds will be able to create such an account by calling the `CreateClawbackVestingAccount` method and defining a funder address
- vesting and lockup periods can then be created by that funder address using `FundClawbackAccount`

### Patches
_Has the problem been patched? What versions should users upgrade to?_

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_
