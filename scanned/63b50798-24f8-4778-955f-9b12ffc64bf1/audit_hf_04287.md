# [H] H-03 | Users Can Use Shift To Avoid Deposit Fees

## Summary
Severity: High
Contest weight: 0.2664
Dataset id: 21426
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can avoid the SwapPricingType.TwoStep fee on deposits by utilizing shift and its lack of fees. Inside _executeDeposit, SwapPricingUtils.getSwapFees calculates the fee that users would pay for depositing into the exchange. Where there are 3 fees - TwoStep, Atomic, and 0 fee for shifts. Users can abuse the lack of fee for shifts by simply front-running the keeper and sending their desired tokens to the shiftVault. When the keeper calls executeShift, these tokens would be accounted for as deposited from the shift when recordTransferIn is executed. This way, users can avoid paying the SwapPricingType.TwoStep fee. For Example: 1. User makes a deposit of 1 USDC into the USDC:WETH vault. 2. User creates a shift for the same market. 3. User sees keeper TX and front-runs with 10,000 USDC and 2 WETH. 4. Keeper executes shift: 1. In the middle of the shift after the withdrawal, the tokens are recorded from the ShiftVault. 2. The recorded change is 10,001 USDC and 2 WETH. 5. The shift deposits the USDC and WETH while avoiding the fee.

## Proof of Concept
https://github.com/GuardianAudits/gmx-v2-1-team-2-pocs/tree/POC_FREE_DEPOSIT

## Recommendation
Call shiftVault.recordTransferIn for the long and short tokens when starting executeShift to account for any tokens sent directly to it.
