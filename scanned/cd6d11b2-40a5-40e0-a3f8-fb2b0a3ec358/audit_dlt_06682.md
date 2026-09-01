# [H] CompoundRewards Can Destabilize Vault Leverage to Trigger Subsidy Farming

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-07-04
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/321
Type: hats-finding

## Details
**Github username:** @MehdiKarimi81
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/MahdiKarimi)

  **Beneficiary:** 0xaEAf140B72Aef87a097b67797b711863833534ea
  **Submission hash (on-chain):** 0x748df67f21cd39f022f2654fd34ec2d94a9ff7e144767893962d22028250b23b
  **Severity:** high
  
  **Description:**
  The `DLoopCoreBase` contract implements a **subsidy mechanism** that rewards users for rebalancing the vault’s leverage toward a target. This reward is paid in the form of a **subsidy bonus**, which compensates the caller for performing an economically valuable action: aligning the vault's leverage ratio.

Separately, the `compoundRewards()` function in `RewardClaimable` allows users to send **debt tokens (exchange asset)** into the contract in exchange for **reward tokens**. Internally, these debt tokens are used to **repay the vault’s outstanding debt**, effectively reducing interest accumulation and adjusting the leverage ratio.

However, this repayment can **interfere** with the vault’s target leverage balance. Specifically:

* The vault may initially be fully balanced (within leverage bounds).
* A user calls `compoundRewards()` and repays some debt.
* This artificially shifts the vault’s leverage **away from the target**.
* Now the vault appears imbalanced and **subsidy becomes claimable again**.
* A user (possibly the same one) can immediately call `increaseLeverage()` or `decreaseLeverage()` to rebalance — and **earn a subsidy reward that they themselves made possible**.

A proper safeguard should enforce that `compoundRewards()` can only be called when it moves current leverage towards the target leverage 
---

### Scenario

#### Setup

* **Target leverage:** 3× (30000 bps)
* **Max subsidy:** 10% (`maxSubsidyBps = 1000`)
* **Vault initial state:**

  * Collateral: 100 ETH (worth 200,000 dUSD)
  * Debt: 100,000 dUSD
  * Leverage = 200,000 / (200,000 – 100,000) = **2×**
  * Vault is **already perfectly rebalanced** using `increaseLeverage()`

#### Step 1: Vault is Balanced

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/321_
