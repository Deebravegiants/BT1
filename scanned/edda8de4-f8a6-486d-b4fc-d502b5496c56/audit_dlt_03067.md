# [M] `TapiocaOptionLiquidityProvision` causes Loss of Yield when depositing and withdrawing from Singularity - should use shares to track balances

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1246
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L184-L187


# Vulnerability details

Yieldbox accounts for funds in terms of shares

It does so by looking at TotalDeposited / TotalSupply

When a user deposits `amount`, YieldBox computes the shares to move and moves them to `TapiocaOptionLiquidityProvision`

`TapiocaOptionLiquidityProvision` then records, `amount`

This creates a scenario in which the same amount is actually worth different shares.

### POC

- Depositor A at time 0 of 10 AMT is 10 shares
- Depositor B at time 10 of 10 AMT is 1 share


LP Providers are passing in toShare at the time of deposit

https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L184-L187

```solidity
        // Transfer the Singularity position to this contract
        uint256 sharesIn = yieldBox.toShare(sglAssetID, _amount, false);

        yieldBox.transfer(msg.sender, address(this), sglAssetID, sharesIn);
        activeSingularities[_singularity].totalDeposited += _amount;
```

But they get `amount` recorded instead of Shares


When Unlocked

https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L235-L247
```solidity
        // Transfer the tOLR tokens back to the owner
        sharesOut = yieldBox.toShare(
            lockPosition.sglAssetID,
            lockPosition.amount, /// @audit amount has changed if any yield was generated
            false
        );

        yieldBox.transfer(
            address(this),
            _to,
            lockPosition.sglAssetID,
            sharesOut
        );
```

They get `sharesOut`, which converts amount to shares, but they do not get the Yield generated from that position

### Mitigation

To maintain the invariants of YieldBox, only SHARES should ever be used

Great effort was put into security YieldBox, using `amount` instead of `shares` nullifies that effort

`
        activeSingularities[_singularity].totalDeposited -= lockPosition.shares; /// @audit use shares instead of amount
`


## Assessed type

MEV
