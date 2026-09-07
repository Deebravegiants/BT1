# [H] PowerFarm liquidation impposible due to deprecated nftPosition function

## Summary
Severity: High
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-15
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/35
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x8c418a5f744f3b33e1e0c66bca32338fce2576883d5dea444f9a04be8b97bb69
**Severity:** high

**Description:**
**Description**\
In

```

function _validateIsolationPoolLiquidation(
        address _caller,
        uint256 _nftId,
        uint256 _nftIdLiquidator
    )
        internal
        view
    {
        _onlyIsolationPool(
            _caller
        );

        if (positionLocked[_nftId] == false) {
            revert NotPowerFarm();
        }

        _checkLiquidatorNft(
            _nftId,
            _nftIdLiquidator
        );

        if (POSITION_NFT.getOwner(_nftId) != _caller) {
            revert InvalidCaller();
        }
    }
```


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/35_
