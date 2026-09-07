# [M] Users can self liquidate themselves and avoid any liquidation penalty

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-08-21
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/27
Type: hats-finding

## Details
**Github username:** --
**Submission hash (on-chain):** 0x90ed38375dfc65a9b20b40688e45e234c1e7c0d7ec669a5e081b741d1a61d3f4
**Severity:** medium

**Description:**
**Description**

In `VaultOsToken.sol.liquidateOsToken`, a user can evade liquidation penalties by self-liquidating. Since there is no access control to prevent users from self-liquidating, users can monitor the mempool and submit a liquidation transaction with higher gas fees to prevent excessive asset seizure by a liquidator. 

**Attack Scenario**

An attacker with a low loan-to-value (LTV) ratio could monitor the mempool for transactions set to trigger liquidation. The attacker could then submit a self-liquidation transaction with a higher gas fee, effectively jumping to the front of the transaction queue and liquidating their own assets. This bypasses the liquidation penalty that the protocol may enforce when a liquidator takes over the assets.

**Recommendation**

To mitigate this type of attack, it's recommended to add a liquidation fee that's enforced by the protocol. While this won't necessarily prevent self-liquidation, it would introduce a minimum penalty for users who try to game the system with low LTV ratios. This becomes especially important in a permissionless context like StakeWise where anyone can interact with the protocol.
