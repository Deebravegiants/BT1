# [M] VLT-3 | Deposits Can Be Griefed

## Summary
Severity: Medium
Contest weight: 0.1389
Dataset id: 20590
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the depositIntoEigan function, a user can to deposit an arbitrary amount of vault assets into EigenLayer. This being permissionless, allows the protocol to gain yield more efficiently because it will not have to wait for a trusted party to move these funds. The issue, however, is that the amount that is being deposited is not guaranteed to be available. If another user wanted to grief the protocol, they could do so by frontrunning a call to the depositIntoEigan function by calling the withdrawUsingAssets function. They could then withdraw just enough from the vault so that the other user's deposit call will fail. Long term, this can pose a problem for the protocol because the way for users to gain yield through Rest is to have their funds deposited into EigenLayer. If a user can delay and reduce the efficiency with which these funds move to EigenLayer, the less yield the Rest users will receive.

## Recommendation
Consider having a depositIntoEigan function which deposits the balanceOf(address(this)) instead of a specified amount. This will prevent any grieving of deposits.
