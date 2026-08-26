# [H] Reward computation is wrong

## Summary
Severity: High
Chain: Smart contract
Component: 2021-07-wildcredit
Published: 2021-07-14
Source: https://github.com/code-423n4/2021-07-wildcredit-findings/issues/116
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

The `LendingPair.accrueAccount` function distribtues rewards **before** updating the cumulative supply / borrow indexes as well as the index + balance for the user (by minting supply tokens / debt).
This means the percentage of the user's balance to the total is not correct as the total can be updated several times in between.


```solidity
function accrueAccount(address _account) public {
  // distributes before updating accrual state
  _distributeReward(_account);
  accrue();
  _accrueAccountInterest(_account);

  if (_account != feeRecipient()) {
    _accrueAccountInterest(feeRecipient());
  }
}
```

**Example**: Two users deposit the same amounts in the same block. Thus, after some time they should receive the same tokens.
1. User A and B deposit 1000 tokens (in the same block) and are minted 1000 tokens in return. Total supply = `2000`
2. Assume after 50,000 blocks, `A` calls `accrueAccount(A)` which first calls `_distributeReward`. A is paid out 1000/2000 = 50% of the 50,000 blocks reward since deposit. Afterwards, `accrue` + `_accrueAccountInterest(A)` is called and `A` is minted 200 more tokens due to supplier lending rate. The supply **totalSupply is now 2200**.
3. After another 50,000 blocks, `A` calls `accrueAccount(A)` again. which first calls `_distributeReward`. A is paid out 1200/2200 = **54.5454% of the 50,000 blocks reward since deposit.**

From here, you can already see that `A` receives more than 50% of the 100,000 block rewards although they deposited at the same time as `B` and didn't deposit or withdraw any funds.
`B` will receive `~1000/2200 = 45%` (ignoring any new LP supply tokens minted for `A`'s second claim.)

## Impact
Wrong rewards will be minted for the users which do not represent their real fair share.
Usually, users will get fewer rewards than they should receive as their individual interest was not updated yet but the totals (total debt and total supply) could have been updated by other accounts in between.

## Recommended Mitigation Steps
There are two issues that both contribute to it:

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-07-wildcredit-findings/issues/116_
