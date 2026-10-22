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

This check here will always fail 

```
        if (POSITION_NFT.getOwner(_nftId) != _caller) {
            revert InvalidCaller();
        }
```
getOwner seems to be a function which was present in a past codebase doing the same thing as ERC721's ownerOf so ownerOf should be used instead.


**Attack Scenario**\
No one can liquidate any powerfarm. You can take a freeroll with max leverage and dont fear any liquidation. This can result in bad debt for the system.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
