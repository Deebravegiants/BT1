# [M] GLOBAL-1 | Centralization Risk

## Summary
Severity: Medium
Contest weight: 0.0861
Dataset id: 9326
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The admin address holds the ability to negatively impact the system in numerous ways, including but not limited to:
Take all esGMX, sGMX and bnGMX via reserveSignalTransfer and signalTransfer.
Use the withdrawTokens function to take any non-WETH ERC20 rewarded to the TransferReceiver.
Lock all staked Uniswap V3 LP positions by pausing the LPStaker contract.
Lock all GMXKey and MPKey stakes by pausing the Staker contract.
Raise fees to 100% in the Rewards contract.

## Recommendation
Ensure that the admin address is a multi-sig, optionally with a timelock for improved community trust and oversight. Attempt to limit the scope of the admin address permissions such as locking stakes and raising fees to 100%.
