# [H] openPosition

## Summary
Severity: High
Contest weight: 1.0000
Dataset id: 19641
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When `openPosition()`, we need to record the current `feeGrowthInside0LastX128/feeGrowthInside1LastX128`. And when closing the position, we use `Base.getOwedFee()` to calculate the possible fees generated during the borrowing period, which are used to pay the `LP`.

`openPosition()` -> `Base.prepareLeverage()`
    
```solidity
    function openPosition(
        DataStruct.OpenPositionParams calldata params
    ) public override nonReentrant returns (uint96 lienId, uint256 collateralTo) {
        if (params.liquidity == 0) revert Errors.InsufficientBorrow();

        // local cache to avoid stack too deep
        DataCache.OpenPositionCache memory cache;

        // prepare data for swap
        (
            cache.tokenFrom,
            cache.tokenTo,
            cache.feeGrowthInside0LastX128,
            cache.feeGrowthInside1LastX128,
            cache.collateralFrom,
            collateralTo
        ) = Base.prepareLeverage(params.tokenId, params.liquidity, params.zeroForOne);
...
        liens[keccak256(abi.encodePacked(msg.sender, lienId = _nextRecordId++))] = Lien.Info({
            tokenId: uint40(params.tokenId),
            liquidity: params.liquidity,
            token0PremiumPortion: cache.token0PremiumPortion,
            token1PremiumPortion: cache.token1PremiumPortion,
            startTime: uint32(block.timestamp),
            feeGrowthInside0LastX128: cache.feeGrowthInside0LastX128,
            feeGrowthInside1LastX128: cache.feeGrowthInside1LastX128,
            zeroForOne: params.zeroForOne
        });
```

```solidity
    function prepareLeverage(
        uint256 tokenId,
        uint128 liquidity,
        bool zeroForOne
    )
        internal
        view
        returns (
            address tokenFrom,
            address tokenTo,
            uint256 feeGrowthInside0LastX128,
            uint256 feeGrowthInside1LastX128,
            uint256 collateralFrom,
            uint256 collateralTo
        )
    {
...
        ,
        feeGrowthInside0LastX128,
        feeGrowthInside1LastX128,
        ,

        ) = UNI_POSITION_MANAGER.positions(tokenId);
    }
```

From the above code, we can see that the final value saved to `liens[].feeGrowthInside0LastX128/feeGrowthInside1LastX128` is directly taken from `UNI_POSITION_MANAGER.positions(tokenId)`.

The problem is: The value in `UNI_POSITION_MANAGER.positions(tokenId)` is not the latest.

Only when executing `UNI_POSITION_MANAGER.increaseLiquidity()/decreaseLiquidity()/collect()` will it synchronize the `pool`’s `feeGrowthInside0LastX128/feeGrowthInside1LastX128`.

Because of using the stale value, it leads to a smaller value relative to the actual value. When `closePosition()`, the calculated difference will be larger, and the `borrower` will pay extra fees.

## Proof of Concept
The following test code demonstrates that after `swap()`, `UNI_POSITION_MANAGER.positions(tokenId)` is not the latest unless actively executing `UNI_POSITION_MANAGER.collect()`.

Add to `Swap.t.sol`:
    
```solidity
    function testShowCache() public {
        (,,,,,,,,uint256 feeGrowthInside0LastX128,uint256 feeGrowthInside1LastX128,,) = nonfungiblePositionManager.positions(_tokenId);
        console.log("feeGrowthInside0LastX128(first):",feeGrowthInside0LastX128);
        console.log("feeGrowthInside1LastX128(first):",feeGrowthInside1LastX128);         
        _swap();
        (,,,,,,,,uint256 feeGrowthInside0LastX128Swap,uint feeGrowthInside1LastX128Swap,,) = nonfungiblePositionManager.positions(_tokenId);
        console.log("equal 0 (after swap):",feeGrowthInside0LastX128Swap == feeGrowthInside0LastX128);
        console.log("equal 1 (after swap):",feeGrowthInside1LastX128Swap == feeGrowthInside1LastX128);
        vm.startPrank(LP);
        particlePositionManager.collectLiquidity(_tokenId);
        vm.stopPrank();          
        (,,,,,,,,uint256 feeGrowthInside0LastX128After,uint256 feeGrowthInside1LastX128After,,) = nonfungiblePositionManager.positions(_tokenId);
        console.log("feeGrowthInside0LastX128(after collect):",feeGrowthInside0LastX128After);
        console.log("feeGrowthInside1LastX128(after collect):",feeGrowthInside1LastX128After); 
        
        console.log("feeGrowthInside0LastX128(more):",feeGrowthInside0LastX128After - feeGrowthInside0LastX128);
        console.log("feeGrowthInside1LastX128(more):",feeGrowthInside1LastX128After - feeGrowthInside1LastX128);
    }
```

```bash
forge test -vvv --match-test testShowCache --fork-url https://eth-mainnet.g.alchemy.com/v2/xxxxx --fork-block-number 18750931
```

Logs:
```
  feeGrowthInside0LastX128(first): 72311088602808532523286912166257
  feeGrowthInside1LastX128(first): 29354860053667370145800991738605288969228
  equal 0 (after swap): true
  equal 1 (after swap): true
  feeGrowthInside0LastX128(after collect): 72311299261479720625185125361673
  feeGrowthInside1LastX128(after collect): 29354860053667370145800991738605288969228
  feeGrowthInside0LastX128(more): 210658671188101898213195416
  feeGrowthInside1LastX128(more): 0
```

## Recommendation
After `LiquidityPosition.collectLiquidity()`, execute `Base.prepareLeverage()` to ensure the latest `feeGrowthInside0LastX128/feeGrowthInside1LastX128`.
    
```solidity
    function openPosition(
        DataStruct.OpenPositionParams calldata params
    ) public override nonReentrant returns (uint96 lienId, uint256 collateralTo) {
        if (params.liquidity == 0) revert Errors.InsufficientBorrow();

        // local cache to avoid stack too deep
        DataCache.OpenPositionCache memory cache;

        // decrease liquidity from LP position, pull the amount to this contract
        (cache.amountFromBorrowed, cache.amountToBorrowed) = LiquidityPosition.decreaseLiquidity(
            params.tokenId,
            params.liquidity
        );
        LiquidityPosition.collectLiquidity(
            params.tokenId,
            uint128(cache.amountFromBorrowed),
            uint128(cache.amountToBorrowed),
            address(this)
        );
        // prepare data for swap
         (
            cache.tokenFrom,
            cache.tokenTo,
            cache.feeGrowthInside0LastX128,
            cache.feeGrowthInside1LastX128,
            cache.collateralFrom,
            collateralTo
         ) = Base.prepareLeverage(params.tokenId, params.liquidity, params.zeroForOne);
```
