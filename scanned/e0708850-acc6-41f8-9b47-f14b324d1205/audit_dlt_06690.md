# [H] DLoopDepositorBase Transfers User's Leftover Debt Tokens to Vault Instead of User

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-27
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/275
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/0xvd)

  **Beneficiary:** 0x23B5FbcF9dc2C5d5D6fDCd36d2239E6fC3aED2BA
  **Submission hash (on-chain):** 0x8e67d4e5dd20c45ec7e1455c7d479e2c6d87781254c4c9e7e8305fb76c8c369f
  **Severity:** high
  
  **Description:**
  **Description**\
The DLoopDepositorBase.deposit() function systematically misappropriates leftover debt tokens that belong to users. 

During the deposit process, when flash-loaned debt tokens are swapped for collateral tokens and deposited into the DLoop vault, any remaining debt tokens from favorable swap rates or vault overborrowing are transferred to the dLoopCore contract instead of being returned to the user who initiated the deposit.

In the _handleLeftoverDebtTokens() function, leftover debt tokens are sent to the vault where they reduce the vault's overall debt, benefiting all shareholders proportionally rather than the specific user who generated these leftovers through their deposit transaction. 

This represents a direct loss of user funds, as these tokens have immediate monetary value and rightfully belong to the depositing user.

The issue occurs in every deposit transaction where favorable swap rates or vault mechanics result in leftover debt tokens, making this a systematic fund diversion affecting all users of the DLoopDepositor periphery contracts.

**Attack Scenario**\
User Initiates Deposit: Alice deposits 100 WETH through DLoopDepositorOdos to get 3x leveraged exposure

Flash Loan Execution: Contract flash loans 400,000 dUSD to purchase additional collateral

Favorable Swap Rate: Due to favorable market conditions, only 399,000 dUSD is needed to acquire 200 WETH

Vault Deposit: Contract deposits 300 WETH total, vault borrows 400,000 dUSD and returns it

Flash Loan Repayment: Contract repays 400,000 dUSD

Leftover Calculation: Remaining balance = 400,000 - 399,000 + 400,000 - 400,000 = 600 dUSD

Misappropriation: The 1000 dUSD leftover is transferred to the vault instead of Alice

Value Loss: Alice loses 600 dUSD that should have been returned to her

This scenario can be repeated by any user and scales with deposit frequency and favorable market conditions, resulting in systematic loss of user funds.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/275_
