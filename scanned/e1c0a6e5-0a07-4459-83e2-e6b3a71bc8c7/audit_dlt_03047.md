# [M] In case of Loss to the Yearn Vault, the Contract will stop working until the loss is repaid

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1456
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/yearn/YearnStrategy.sol#L105


# Vulnerability details

Yearn V2 and V3 have the concept of Lossy Strategies, these are dealt with by imputing the loss to the caller.

https://github.com/yearn/yearn-vaults/blob/97ca1b2e4fcf20f4be0ff456dabd020bfeb6697b/contracts/Vault.vy#L1030-L1034

```python
@external
@nonreentrant("withdraw")
def withdraw(
    maxShares: uint256 = MAX_UINT256,
    recipient: address = msg.sender,
    maxLoss: uint256 = 1,  # 0.01% [BPS]
) -> uint256:
```


When the YearnStrategy calls `withdraw` with a third parameter set to 0, it means that the withdrawer isn't willing to take any loss.
https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/yearn/YearnStrategy.sol#L105

```solidity
vault.withdraw(toWithdraw, address(this), 0);
```

This can cause a DOS when it matters, because while the Owner can call `emergencyWithdraw`, because the loss is set to 0, this can cause the vault shares to be stuck until the loss is either repaid or socialized

### POC

- Deposit in Yearn Vault
- Vault has strategy with loss
- Call `vault.withdraw(toWithdraw, address(this), 0);`
- Strategy has loss
- Check causes revert

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1456_
