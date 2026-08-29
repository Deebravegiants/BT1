# [M] Vaults can be created and used with zero governance fee

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-25
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/36
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x9392cc65642fa3e49ff9c6b94b5b9cb7b8a6731d70b948bc27f964cfc43b4052
**Severity:** medium

**Description:**
**Description**\
On `CatalystFactory` deployment, the `_defaultGovernanceFee` remains 0, a separate `setDefaultGovernanceFee` function is used to set the governance fee.

The value of `_defaultGovernanceFee` is passed to the vault during its creation.

Notorious vault deployers can misuse this mechanism to create vaults with 0 fee by frontrunning the `setDefaultGovernanceFee` call and deploying the vaults before default governance fee gets initialized. These vaults can now be freely used by parties without paying any governance fee.

I am aware that factory owner can set the fee for those vaults later. But as per the comments [here](https://github.com/catalystdao/catalyst/blob/main/evm/src/CatalystVaultCommon.sol#L148)
>      * !CatalystFactory(_factory).owner() must be set to a timelock!

it can be seen that the factory owner will be governance/timelock contract. So setting fee for those new vaults will become a time delayed operation. The longer the delay in setting fee for vaults more will be the protocol fee loss for Catalyst protocol owners.


**Attack Scenario**\
1. Factory gets deployed.
2. Before default fee gets set, new vaults get deployed.
3. Those new vaults will have 0 governance fee.

**Attachments**

1. **Proof of Concept (PoC) File**
NA

2. **Revised Code File (Optional)**

    Consider setting the default fee value in Factory's constructor.
