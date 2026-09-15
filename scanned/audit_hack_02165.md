# [M] Tokens with fee on transfer are not supported

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2021-11-vader/blob/429970427b4dc65e37808d7116b9de27e395ce0c/contracts/dex-v2/pool/BasePoolV2.sol#L168-L229
Type: audit-issue

## Details
# Handle

WatchPug


# Vulnerability details

There are ERC20 tokens that charge fee for every `transfer()` or `transferFrom()`, E.g `Vader` token.

In the current implementation, `BasePoolV2.sol#mint()` assumes that the received amount is the same as the transfer amount, and uses it to calculate liquidity units.

https://github.com/code-423n4/2021-11-vader/blob/429970427b4dc65e37808d7116b9de27e395ce0c/contracts/dex-v2/pool/BasePoolV2.sol#L168-L229

```solidity=168
function mint(
    IERC20 foreignAsset,
    uint256 nativeDeposit,
    uint256 foreignDeposit,
    address from,
    address to
)
    external
    override
    nonReentrant
    onlyRouter
    supportedToken(foreignAsset)
    returns (uint256 liquidity)
{
    (uint112 reserveNative, uint112 reserveForeign, ) = getReserves(
        foreignAsset
    ); // gas savings

    nativeAsset.safeTransferFrom(from, address(this), nativeDeposit);
    foreignAsset.safeTransferFrom(from, address(this), foreignDeposit);

    PairInfo storage pair = pairInfo[foreignAsset];
    uint256 totalLiquidityUnits = pair.totalSupply;
    if (totalLiquidityUnits == 0) liquidity = nativeDeposit;
    else
        liquidity = VaderMath.calculateLiquidityUnits(
            nativeDeposit,
            reserveNative,
            foreignDeposit,
            reserveForeign,
            totalLiquidityUnits
        );

    require(
        liquidity > 0,
        "BasePoolV2::mint: Insufficient Liquidity Provided"
    );

    uint256 id = positionId++;

    pair.totalSupply = totalLiquidityUnits + liquidity;
    _mint(to, id);

    positions[id] = Position(
        foreignAsset,
        block.timestamp,
        liquidity,
        nativeDeposit,
        foreignDeposit
    );

    _update(
        foreignAsset,
        reserveNative + nativeDeposit,
        reserveForeign + foreignDeposit,
        reserveNative,
        reserveForeign
    );

    emit Mint(from, to, nativeDeposit, foreignDeposit);
    emit PositionOpened(from, to, id, liquidity);
}
```

## Recommended

Consider calling `balanceOf()` to get the actual balances.
