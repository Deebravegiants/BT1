# [M] `_updateSettlementPostBurn`

## Summary
Severity: Medium
Contest weight: 0.8232
Dataset id: 21231
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
s_grossPremiumLast[]` definitions are as follows:

/// @dev Per-chunk `last` value that gives the aggregate amount of premium owed to all sellers when multiplied by the total amount of liquidity `totalLiquidity`  
/// totalGrossPremium = totalLiquidity * (grossPremium(perLiquidityX64) - lastGrossPremium(perLiquidityX64)) / 2**64  
/// Used to compute the denominator for the fraction of premium available to sellers to collect  
/// LeftRight - right slot is token0, left slot is token1  
mapping(bytes32 chunkKey => LeftRightUnsigned lastGrossPremium) internal s_grossPremiumLast;

A critical rule: if there is a change in `totalLiquidity`, we must recalculate this value.

When `Pool.mintOptions()`, `s_grossPremiumLast[chunkKey]` will increase.

Step: `mintOptions()`->`_mintInSFPMAndUpdateCollateral()`->`_updateSettlementPostMint()`
    
    function _updateSettlementPostMint(
        TokenId tokenId,
        LeftRightUnsigned[4] memory collectedByLeg,
        uint128 positionSize
    ) internal {
    ...
        if (tokenId.isLong(leg) == 0) { 
            LiquidityChunk liquidityChunk = PanopticMath.getLiquidityChunk(
                tokenId,
                leg,
                positionSize
            );
    ...
            uint256[2] memory grossCurrent;
            (grossCurrent[0], grossCurrent[1]) = SFPM.getAccountPremium(
                address(s_univ3pool),
                address(this),
                tokenId.tokenType(leg),
                liquidityChunk.tickLower(),
                liquidityChunk.tickUpper(),
                type(int24).max,
                0
            );

            unchecked {
                // L
                LeftRightUnsigned grossPremiumLast = s_grossPremiumLast[chunkKey];
                // R
                uint256 positionLiquidity = liquidityChunk.liquidity();
                // T (totalLiquidity is (T + R) after minting)
                uint256 totalLiquidityBefore = totalLiquidity - positionLiquidity;

                s_grossPremiumLast[chunkKey] = LeftRightUnsigned
                    .wrap(0)
                    .toRightSlot(
                        uint128(
                            (grossCurrent[0] *
                                positionLiquidity +
                                grossPremiumLast.rightSlot() *
                                totalLiquidityBefore) / (totalLiquidity)
                        )
                    )
                    .toLeftSlot(
                        uint128(
                            (grossCurrent[1] *
                                positionLiquidity +
                                grossPremiumLast.leftSlot() *
                                totalLiquidityBefore) / (totalLiquidity)
                        )
                    );
            }
        }
    }
}
```
When `Pool.burnOptions()`，`s_grossPremiumLast[chunkKey]` will decrease

`burnOptions()`->`_burnAndHandleExercise()`->`_updateSettlementPostBurn()`
    
```solidity
function _updateSettlementPostBurn(
    address owner,
    TokenId tokenId,
    LeftRightUnsigned[4] memory collectedByLeg,
    uint128 positionSize,
    bool commitLongSettled
) internal returns (LeftRightSigned realizedPremia, LeftRightSigned[4] memory premiaByLeg) {
...
    uint256 numLegs = tokenId.countLegs();
    uint256[2][4] memory premiumAccumulatorsByLeg;

    // compute accumulated fees
    (premiaByLeg, premiumAccumulatorsByLeg) = _getPremia(
        tokenId,
        positionSize,
        owner,
        COMPUTE_ALL_PREMIA,
        type(int24).max
    );

    for (uint256 leg = 0; leg < numLegs; ) {
        LeftRightSigned legPremia = premiaByLeg[leg];

        bytes32 chunkKey = keccak256(
            abi.encodePacked(tokenId.strike(leg), tokenId.width(leg), tokenId.tokenType(leg))
        );

        // collected from Uniswap
        LeftRightUnsigned settledTokens = s_settledTokens[chunkKey].add(collectedByLeg[leg]);

        if (LeftRightSigned.unwrap(legPremia) != 0) {
            // (will be) paid by long legs
            if (tokenId.isLong(leg) == 1) {
    ...
            } else {
                uint256 positionLiquidity = PanopticMath
                    .getLiquidityChunk(tokenId, leg, positionSize)
                    .liquidity();

                // new totalLiquidity (total sold) = removedLiquidity + netLiquidity (T - R)
                uint256 totalLiquidity = _getTotalLiquidity(tokenId, leg);
                // T (totalLiquidity is (T - R) after burning)
                uint256 totalLiquidityBefore = totalLiquidity + positionLiquidity;

                LeftRightUnsigned grossPremiumLast = s_grossPremiumLast[chunkKey];

                LeftRightUnsigned availablePremium = _getAvailablePremium(
                    totalLiquidity + positionLiquidity,
                    settledTokens,
                    grossPremiumLast,
                    LeftRightUnsigned.wrap(uint256(LeftRightSigned.unwrap(legPremia))),
                    premiumAccumulatorsByLeg[leg]
                );

                // subtract settled tokens sent to seller
                settledTokens = settledTokens.sub(availablePremium);

                // add available premium to amount that should be settled
                realizedPremia = realizedPremia.add(
                    LeftRightSigned.wrap(int256(LeftRightUnsigned.unwrap(availablePremium)))
                );

    ...

                unchecked {
                    uint256[2][4] memory _premiumAccumulatorsByLeg = premiumAccumulatorsByLeg;
                    uint256 _leg = leg;

                    // if there's still liquidity, compute the new grossPremiumLast
                    // otherwise, we just reset grossPremiumLast to the current grossPremium
                    s_grossPremiumLast[chunkKey] = totalLiquidity != 0
                        ? LeftRightUnsigned
                            .wrap(0)
                            .toRightSlot(
                                uint128(
                                    uint256(
                                        Math.max(
                                            (int256(
                                                grossPremiumLast.rightSlot() *
                                                    totalLiquidityBefore
                                            ) -
                                                int256(
                                                    _premiumAccumulatorsByLeg[_leg][0] *
                                                        positionLiquidity
                                                )) + int256(legPremia.rightSlot() * 2 ** 64),
                                            0
                                        )
                                    ) / totalLiquidity
                                )
                            )
                            .toLeftSlot(
                                uint128(
                                    uint256(
                                        Math.max(
                                            (int256(
                                                grossPremiumLast.leftSlot() *
                                                    totalLiquidityBefore
                                            ) -
                                                int256(
                                                    _premiumAccumulatorsByLeg[_leg][1] *
                                                        positionLiquidity
                                                )) + int256(legPremia.leftSlot()) * 2 ** 64,
                                            0
                                        )
                                    ) / totalLiquidity
                                )
                            )
                        : LeftRightUnsigned
                            .wrap(0)
                            .toRightSlot(uint128(premiumAccumulatorsByLeg[_leg][0]))
                            .toLeftSlot(uint128(premiumAccumulatorsByLeg[_leg][1]));
                }
            }
        }

        // update settled tokens in storage with all local deltas
        s_settledTokens[chunkKey] = settledTokens;

        unchecked {
            ++leg;
        }
```

The issue lies within `_updateSettlementPostBurn()`, where it adds a condition that `if (LeftRightSigned.unwrap(legPremia) != 0)` must be met for `s_grossPremiumLast[chunkKey]` to decrease.

This results in not recalculating `s_grossPremiumLast[chunkKey]` even when `totalLiquidity` changes.

For example, in the same block, if a user executes `mintOptions()`, `s_grossPremiumLast[chunkKey]` increases by 50. Immediately after, executing `burnOptions()` doesn’t decrease `s_grossPremiumLast[chunkKey]` by 50 because `legPremia == 0`.

## Proof of Concept
The following code demonstrates this scenario, where `s_grossPremiumLast[chunkKey]` keeps increasing, so `last gross accumulated` keeps decreasing.

  1. Add to `Misc.t.sol`

```solidity
function test_burn_not_reduce_last() public {
    swapperc = new SwapperC();
    vm.startPrank(Swapper);
    token0.mint(Swapper, type(uint128).max);
    token1.mint(Swapper, type(uint128).max);
    token0.approve(address(swapperc), type(uint128).max);
    token1.approve(address(swapperc), type(uint128).max);

    // mint OTM position
    $posIdList.push(
        TokenId.wrap(0).addPoolId(PanopticMath.getPoolId(address(uniPool))).addLeg(
            0,
            1,
            1,
            0,
            0,
            0,
            15,
            1
        )
    );
    //@info Bob same gross
    vm.startPrank(Bob);
    pp.mintOptions($posIdList, 1_000_000, 0, 0, 0);
    vm.startPrank(Swapper);
    swapperc.swapTo(uniPool, Math.getSqrtRatioAtTick(10) + 1);
    // 1998600539
    accruePoolFeesInRange(address(uniPool), (uniPool.liquidity() * 2) / 3, 1, 1);
    swapperc.swapTo(uniPool, 2 ** 96); 
    //@info end of Bob same gross

    //@info start alice , it should without change gross
    console.log("*****start alice mint/burn should not reduce last accumulated");
    for(uint256 i=0;i<10;i++){
        vm.startPrank(Alice);
        pp.mintOptions($posIdList, 250_000, type(uint64).max, 0, 0);

        vm.startPrank(Alice);
        pp.burnOptions($posIdList[0], new TokenId[](0), 0, 0);
    } 
}    
```

  2. Add to `PanopticPool.sol`

```solidity
function _updateSettlementPostMint(
    TokenId tokenId,
    LeftRightUnsigned[4] memory collectedByLeg,
    uint128 positionSize
) internal {
...
    unchecked {
        // L
        LeftRightUnsigned grossPremiumLast = s_grossPremiumLast[chunkKey];
        // R
        uint256 positionLiquidity = liquidityChunk.liquidity();
        // T (totalLiquidity is (T + R) after minting)
        uint256 totalLiquidityBefore = totalLiquidity - positionLiquidity;
        //console.log("s_grossPremiumLast[chunkKey].rightSlot() from:",s_grossPremiumLast[chunkKey].rightSlot());
        s_grossPremiumLast[chunkKey] = LeftRightUnsigned
            .wrap(0)
            .toRightSlot(
                uint128(
                    (grossCurrent[0] *
                        positionLiquidity +
                        grossPremiumLast.rightSlot() *
                        totalLiquidityBefore) / (totalLiquidity)
                )
            )
            .toLeftSlot(
                uint128(
                    (grossCurrent[1] *
                        positionLiquidity +
                        grossPremiumLast.leftSlot() *
                        totalLiquidityBefore) / (totalLiquidity)
                )
            );
        console.log("last accumulated : ",(grossCurrent[0] - s_grossPremiumLast[chunkKey].rightSlot()) * totalLiquidity);
    }
}
```

    $ forge test -vvv --match-test test_burn_not_reduce_last
    
    [PASS] test_burn_not_reduce_last() (gas: 5276055)
    Logs:
      last accumulated :  0

## Recommendation
No recommendation
