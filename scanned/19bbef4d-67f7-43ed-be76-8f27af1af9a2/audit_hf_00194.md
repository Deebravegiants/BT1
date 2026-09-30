# [M] Incorrect `updateGlobalExchangeRate` implementation

## Summary
Severity: Medium
Contest weight: 0.2242
Dataset id: 1024
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`UpdateGlobalExchangeRate` has incorrect implementation when `totalGlobalShares` is zero.

If any user didn't start stake, `totalGlobalShares` is 0, and every stake it will increase. but there is possibility that `totalGlobalShares` can be 0 amount later by unstake or disable validator.

## Proof of Concept
This is my test case to proof this issue: [C4_issues.js L76](https://github.com/xYrYuYx/C4-2021-10-covalent/blob/main/test/c4-tests/C4_issues.js#L76)

In my test case, I disabled validator to make `totalGlobalShares` to zero. And in this case, some reward amount will be forever locked in the contract. After disable validator, I mined 10 blocks, and 4 more blocks mined due to other function calls, So total 14 CQT is forever locked in the contract.

## Recommendation
Please think again when `totalGlobalShares` is zero.

That is right, and I think the best solution would be to add a validator instance who is the owner and stake some low amount of tokens in it. This way we can make sure there is no such situation when `totalGlobalShares` becomes `0` and if everyone unstaked, the owner could take out reward tokens and then unstake / redeem rewards.

Not sure. That could even be marked as "high risk". if the situation happens and not handled right away (taking out reward tokens), then there could be more significant financial loss.

marked resolved as it will be manually handled

The issue found by the warden is straightforward: Through mix of unstaking and the use of `disableValidator` the warden was able to lock funds, making them irredemeable

It seems to me that this is caused by the fact that `unstake` as well as `disableValidator` will reduce the shares: [https://github.com/code-423n4/2021-10-covalent/blob/a8368e7982d336a4b464a53cfe221b2395da801f/contracts/DelegatedStaking.sol#L348`](https://github.com/code-423n4/2021-10-covalent/blob/a8368e7982d336a4b464a53cfe221b2395da801f/contracts/DelegatedStaking.sol#L348%60)

I would recommend separating the shares accounting from the activation of validator, simply removing the subtraction of global shares in `disableValidator` would allow them to claim those shares.

The function `disableValidator` can be called by either the validator or the owner, while onlyOwner can add a new validator

The owner has the ability to perform this type of griefing, as well as a group of validators if they so chose

Due to the specifics of the grief I will rate it of Medium Severity, as per the docs: `2 — Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.`

In this case we have a way to leak value (lock funds) with specific condition (malicious owner or multiple griefing validators)
