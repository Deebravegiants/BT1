# [H] Liquidation can be escaped by depositing a WJLP with `_rewardOwner` != `_borrower`

## Summary
Severity: High
Chain: Smart contract
Component: 2021-12-yetifinance
Published: 2021-12-22
Source: https://github.com/code-423n4/2021-12-yetifinance-findings/issues/284
Type: code-finding

## Details
# Handle

WatchPug


# Vulnerability details

https://github.com/code-423n4/2021-12-yetifinance/blob/5f5bf61209b722ba568623d8446111b1ea5cb61c/packages/contracts/contracts/TroveManagerLiquidations.sol#L409-L409

```solidity=409
    _updateWAssetsRewardOwner(collsToUpdate, _borrower, yetiFinanceTreasury);
```

In `_liquidateNormalMode()`, WAsset rewards for collToRedistribute will accrue to Yeti Finance Treasury, However, if a borrower wrap `WJLP` and set `_rewardOwner` to other address, `_updateWAssetsRewardOwner()` will fail due to failure of `IWAsset(token).updateReward()`.

https://github.com/code-423n4/2021-12-yetifinance/blob/5f5bf61209b722ba568623d8446111b1ea5cb61c/packages/contracts/contracts/AssetWrappers/WJLP/WJLP.sol#L126-L138

```solidity=126
function wrap(uint _amount, address _from, address _to, address _rewardOwner) external override {
    JLP.transferFrom(_from, address(this), _amount);
    JLP.approve(address(_MasterChefJoe), _amount);

    // stake LP tokens in Trader Joe's.
    // In process of depositing, all this contract's
    // accumulated JOE rewards are sent into this contract
    _MasterChefJoe.deposit(_poolPid, _amount);

    // update user reward tracking
    _userUpdate(_rewardOwner, _amount, true);
    _mint(_to, _amount);
}
```


### PoC

1. Alice `wrap()` some `JLP` to `WJLP` and set `_rewardOwner` to another address;
2. Alice deposited `WJLP` as a collateral asset and borrowed the max amount of YUSD;

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-12-yetifinance-findings/issues/284_
