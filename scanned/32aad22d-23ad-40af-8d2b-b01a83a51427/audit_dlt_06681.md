# [H] Accumulated Interest Redirected as Subsidy Prevents Protocol Profitability

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-07-04
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/323
Type: hats-finding

## Details
**Github username:** @MehdiKarimi81
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/MahdiKarimi)

  **Beneficiary:** 0xaEAf140B72Aef87a097b67797b711863833534ea
  **Submission hash (on-chain):** 0x98e0668570deeb34a1bfb52c9934624984eed2dd5b14d43334e539d22648c415
  **Severity:** high
  
  **Description:**
  The `DLoopCoreDLend` vault accrues interest on its deposited collateral in the lending pool over time. This interest should ideally contribute to vault profitability and increase the share value for long-term users. However, the current design **implicitly redirects all of this interest income toward rebalancing subsidies**.

Because the vault’s leverage is sensitive to minor changes in collateral or debt (including interest accrual), any amount of interest accrued on the supplied collateral **alters the leverage**, triggering **rebalancing opportunities**. These rebalancing calls (via `increaseLeverage()` or `decreaseLeverage()`) are incentivized with a **subsidy payout**, which is effectively sourced from the vault’s own value.

This creates a circular drain:

* Interest is accrued → leverage deviates slightly → someone rebalances → **subsidy is paid** → vault loses equivalent value.

As a result, **the protocol never truly earns** the interest accumulated on the collateral. Instead, it is **immediately extracted** by users through repeated rebalancing and subsidy farming. Over time, this undermines the protocol’s profitability and **prevents sustainable growth**, especially when subsidies are set to their maximum levels.

---

### 🔢 **Numerical Scenario**

#### Setup:

* **Target leverage:** 3× (30000 bps)
* **Vault collateral:** 100 ETH (worth 200,000 dUSD)
* **Vault debt:** 100,000 dUSD
* **Subsidy cap:** 10% (`maxSubsidyBps = 1000`)
* Vault is currently balanced (2× leverage)

#### Step 1: Interest Accrues on Collateral

* Lending pool pays **2% interest annually** to collateral.
* After 1 month, the vault accrues ≈ **333 dUSD** worth of interest (200,000 × 2% ÷ 12).
* New collateral base = 200,333 dUSD; debt remains 100,000 dUSD.
* New leverage: 200,333 / (200,333 – 100,000) ≈ **2.003x**


_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/323_
