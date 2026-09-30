# [M] Rebasing tokens are not supported

## Summary
Severity: Medium
Contest weight: 0.4113
Dataset id: 2598
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The readme states that rebasing tokens are supported
Rebasing tokens are supported with exchange rate mechanism
However, only non rebasing tokens such as the wrapped version wsteth are supposed. If stETH is used, it will accrue value in the Psm and Vault (technically they are the same contract) which will be left untracked as Ra and Pa deposits are tracked in state variables.
The code does not handle rebasing tokens even though the readme says it does. The exchange rate mechanism only supports non rebasing tokens such as wsteth.

Internal pre-conditions
None.

External pre-conditions
None.

Attack Path
Admin creates steth pairs using it as Ra or Pa, whose value will grow in the protocol but left untracked as the quantites are tracked with state variables.
Stuck yield accruel in the Vault/Psm contracts.

## Proof of Concept
State.sol tracks the balances:
```solidity
struct Balances {
    PsmRedemptionAssetManager ra;
    uint256 dsBalance;
    uint256 ctBalance;
    uint256 paBalance;
}
```

## Recommendation
Don't set rebasing tokens as Ra or Pa or implement a way to sync the balances.
