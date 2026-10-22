# [M] Incorrect depositCap check in T

## Summary
Severity: Medium
Contest weight: 0.1778
Dataset id: 1772
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The depositCap check in the _deposit function of the Tranche contract uses an assets amount that includes a fee. However, this fee is transferred out of the vault, meaning it does not contribute to the actual asset amount in the vault and thus should not impact the depositCap.
In the line require(totalAssets()+assets<depositCap,"DEPOSIT_CAP_BREACHED");, the function checks assets without accounting for the deduction of getDepositFeesTotal(assets). As a result, the depositCap check is inflated by the fee amount, potentially causing deposits to be rejected incorrectly when the vault is close to the cap. The check should use assets-fee to accurately reflect the true impact on the vault balance. (here)
Internal pre-conditions
1. The vault is close to reaching its depositCap.
External pre-conditions
None.
Attack Path
1. A user attempts to deposit when the vault is close to its depositCap.
2. Due to the fee being included in the assets amount, the cap check fails, rejecting the deposit unnecessarily.
The current implementation may cause users to be incorrectly prevented from depositing due to an inflated assets value. This issue is more prominent when the vault balance is near the depositCap, as it could block further deposits prematurely.

## Recommendation
Modify the depositCap check to account for the deposit fee by using assets-getDepositFeesTotal(assets), ensuring only the net deposited amount contributes to the cap calculation.
