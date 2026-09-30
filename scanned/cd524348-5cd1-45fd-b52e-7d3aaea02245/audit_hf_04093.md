# [M] GMXUT-1 | Can't Unfreeze Vault If Execution Interrupted

## Summary
Severity: Medium
Contest weight: 0.1471
Dataset id: 20548
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the unwrapping process, the vault is frozen by incrementing the mapping
_vaultToPendingAmountWeiMap by _amountDeltaWei.value.
Once unwrapping concludes, the _vaultToPendingAmountWeiMap function is reduced by
_amountDeltaWei.value, effectively unfreezing the vault.
However, the unwrapping process may fail, as acknowledged in the afterWithdrawalExecution
function:
// @audit: If GMX changes the keys OR if the data sent back is malformed (causing the above requires to
fail), this will fail. This will result in us receiving tokens from GMX and not knowing who they
are for, nor the amount. The only solution will be to upgrade this contract and have an admin
"unstuck" the funds for users by sending them to the appropriate vaults.
In the event of a failure in the afterWithdrawalExecution function, the protocol can recover the funds
but is unable to unfreeze the vault. Consequently, the user remains unable to utilize their vault,
including unwrapping any remaining funds.

## Recommendation
Enable the Admin to invoke the setVaultAccountPendingAmountForFrozenStatus function, providing
a means to unfreeze an account if execution is ever interrupted.
