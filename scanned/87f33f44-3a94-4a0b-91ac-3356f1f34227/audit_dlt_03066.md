# [M] `TapiocaOptionLiquidityProvision` stores amount which cause Socialization of Loss when unlocking

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1247
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L184-L187


# Vulnerability details

### Impact
LP Providers are passing in toShare at the time of deposit

https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L184-L187

```solidity
        // Transfer the Singularity position to this contract
        uint256 sharesIn = yieldBox.toShare(sglAssetID, _amount, false);

        yieldBox.transfer(msg.sender, address(this), sglAssetID, sharesIn);
        activeSingularities[_singularity].totalDeposited += _amount;
```

But they get `amount` recorded instead of Shares

While shares cannot be manipulated, `amount` could.

If a strategy relies on the value of it's Yield, or `strategy._currentBalance` is manipulatable, then an incorrect `amount` could be recorded either during a deposit or a withdrawal

When Unlocked, if the YieldBox had a Loss, or the Price is Manipulated then the `amount` will be withdrawn, but it will result in a loss of shares from other depositors 

https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L235-L247

```solidity
        // Transfer the tOLR tokens back to the owner
        sharesOut = yieldBox.toShare(
            lockPosition.sglAssetID,
            lockPosition.amount, /// @audit amount is converted to `shares`, the exchange rate may be manipulated
            false
        );

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1247_
