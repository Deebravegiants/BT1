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

        yieldBox.transfer(
            address(this),
            _to,
            lockPosition.sglAssetID,
            sharesOut
        );
    activeSingularities[_singularity].totalDeposited -= lockPosition.amount; /// @audit Amount is subtracted, resulting in more shares burned than the original deposit
```

They burn `sharesOut`, which may be more shares than what they originally deposited, socializing a loss to all other depositors

### POC - Strategy incurrs a Loss
- User A and B each Deposit 10 Shares
- Total Supply = 20 shares
- Total Amount = 20
- Slash / Cause a loss to strategy (e.g. slippage, manipulation or outright theft), loss of 50%
- User A withdraws `10 amount`, this burns `20 shares`
- User B has a `lockPosition.amount` of `10 amount`, but the contract has no shares left, they lost their deposit

### POC 2 - Inflating amount to steal other people shares
- User A and B each Deposit 10 Shares
- Total Supply = 20 shares
- Total Amount = 20
- A Inflates the value of shares, perhaps by using a vulnerable strategy (demonstrated separately)
- A records a `20 amount` when they deposited only `10 shares`
- A withdraws the `20 amount`, and get's all the shares, B is stuck with a `lockPosition.amount` of  `10` but no shares to withdraw from

### Mitigation

To maintain the invariants of YieldBox, only SHARES should ever be used to track positions

`
        activeSingularities[_singularity].totalDeposited -= lockPosition.shares;
`

This will rely on the proven invariant of YieldBox properly tracking each deposit

Instead, amounts can be manipulated to cause loss


## Assessed type

MEV
