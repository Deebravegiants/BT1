# [M] Lender.sol: Incorrect rewards accounting for

## Summary
Severity: Medium
Contest weight: 0.1231
Dataset id: 20359
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When interest is accrued, the RESERVE address gets minted shares. However the Lender._transfer function does not accrue interest and so RESERVE's balance is not up to date which means the Rewards.updateUserState call operates on an incorrect balance. The balance of RESERVE is too low which results in a loss of rewards. As described above, the RESERVE address should have its reward accounting done correctly just like all other addresses. Failing to do so means that the RESERVE misses out on some rewards because Lender._transfer does not update the share balance correctly and so the rewards will be accrued on a balance that is too low.

## Recommendation
The RESERVE address should be special-cased in the Lender._transfer function. Thereby gas is saved when transfers are executed that do not involve the RESERVE address and the reward accounting is done correctly for when the RESERVE address is involved. When the RESERVE address is involved, (Cache memory cache, ) = _load(); and _save(cache, /* didChangeBorrowBase: */ false); must be called. Also the Rewards state must be updated with this call: Rewards.updatePoolState(s, a, newTotalSupply);.
