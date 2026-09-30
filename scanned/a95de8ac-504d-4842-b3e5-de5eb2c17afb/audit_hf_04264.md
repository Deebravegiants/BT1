# [M] `_validatePositionList`

## Summary
Severity: Medium
Contest weight: 0.3002
Dataset id: 21227
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The underlying issue is that `_validatePositionList()` does not check for duplicate tokenIds. Attackers can use this issue to bypass solvency checks, which leads to several impacts:

1. Users can mint/burn/liquidate/forceExercise when they are insolvent.
2. Users can settleLongPremium/forceExercise another user when the other user is insolvent.

This also conflicts a main invariant stated in audit readme: `Users should not be allowed to mint/burn options or pay premium if their end state is insolvent`.

## Proof of Concept
In this report, we will only prove the core issue: duplicate tokenIds are allowed, and won’t craft complicated scenarios for relevant impacts.

Add the following test code in `PanopticPool.t.sol`, we can see that passing 257 of the same token ids can still work for `mintOptions()`.
    
    function test_duplicatePositionHash(
        uint256 x,
        uint256[2] memory widthSeeds,
        int256[2] memory strikeSeeds,
        uint256[2] memory positionSizeSeeds,
        uint256 swapSizeSeed
    ) public {
        _initPool(x);

        (int24 width, int24 strike) = PositionUtils.getOTMSW(
            widthSeeds[0],
            strikeSeeds[0],
            uint24(tickSpacing),
            currentTick,
            0
        );

        (int24 width2, int24 strike2) = PositionUtils.getOTMSW(
            widthSeeds[1],
            strikeSeeds[1],
            uint24(tickSpacing),
            currentTick,
            0
        );
        vm.assume(width2 != width || strike2 != strike);

        populatePositionData([width, width2], [strike, strike2], positionSizeSeeds);

        // leg 1
        TokenId tokenId = TokenId.wrap(0).addPoolId(poolId).addLeg(
            0, 1, isWETH, 0, 0, 0, strike, width
        );

        TokenId[] memory posIdList = new TokenId[](257);
        for (uint i = 0; i < 257; ++i) {
            posIdList[i] = tokenId;
        }
        pp.mintOptions(posIdList, positionSizes[0], 0, 0, 0);
    }

## Recommendation
Add a check in `_validatePositionList` that the length is shorter than `MAX_POSITIONS` (32).
