# [M] PerpDepository#_rebalanceNegativePnlWith-

## Summary
Severity: Medium
Contest weight: 0.3726
Dataset id: 19789
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Throughout the entirety of the contract it grants approval to the vault before depositing either quote or asset. In this case there is no approval which means that the deposit call will fail causing PerpDepository#_rebalanceNegativePnlWithSwap to always revert.
See summary.
PerpDepository#_rebalanceNegativePnlWithSwap won't function

## Recommendation
Add the missing approve call:
```solidity
} else if (shortFall < 0) {
    // we got excess tokens in the spot swap. Send them to the account paying for rebalance
    IERC20(quoteToken).transfer(
        account,
        _abs(shortFall)
    );
}
```
