# [H] `_getPositionTVL` of `UNIv3Connector` wrongly assumes ownership of all liquidity of the provided ticks inside `positionManager`

## Summary
Severity: High
Contest weight: 0.6643
Dataset id: 21215
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the TVL calculation routine of the UniV3 connector, specifically the internal function that determines the value of a position. The routine queries the Uniswap V3 pool for the total liquidity that exists between two tick boundaries and then assumes that the entire amount of liquidity returned belongs to the connector’s own position. This assumption is incorrect because the pool aggregates liquidity from all participants that share the same tick range, regardless of who owns each share. The root cause is the construction of a pool position key from the connector’s position manager address together with the lower and upper tick values, and then calling pool.positions with that key. The key does not identify a single NFT or a specific owner; it identifies the whole tick range, so the liquidity value includes contributions from unrelated LPs. An attacker can exploit this by creating a separate UniV3 position that uses the same tick range but is owned by a different address. When the connector later calls the TVL function, it will read the combined liquidity, add it to its own reported assets, and thereby inflate the protocol’s total value locked. This inflated TVL can be used by the protocol’s accounting logic to grant higher borrowing limits, distribute larger fees, or present a healthier solvency picture to users and investors. The impact is that the protocol may appear to hold more assets than it actually does, leading to potential over‑leveraging and, in worst‑case scenarios, insufficient funds to satisfy withdrawals or settle debts. The condition occurs every time the _getPositionTVL function is invoked, which is typically during deposit, withdrawal, or valuation operations. All users of the protocol, lenders, and token holders are affected because the mis‑reported numbers can change the economic outcomes of their interactions. The issue was discovered during a Code4rena audit when the reviewer examined the logic that builds the pool position key and noticed that it does not verify ownership of the liquidity. The bug is subtle because the function returns a plausible numeric TVL; without a separate sanity check, the over‑statement can go unnoticed. To remediate the problem, the connector should query the positions manager’s positions getter, which returns the exact liquidity owned by the connector’s NFT, or otherwise track the tokenId‑specific liquidity directly, ensuring that only the connector’s own share is counted. This class of bug falls under incorrect accounting of shared resources, where exclusive ownership is incorrectly assumed, leading to inflated asset valuations and potential protocol insolvency. From a user’s perspective the symptom may be that a deposited position is displayed with a higher value than the amount that can actually be withdrawn, or that after a withdrawal the balance unexpectedly drops to zero because the protocol had counted liquidity that was never its own.

## Proof of Concept
```solidity
function _getPositionTVL(HoldingPI memory p, address base) public view override returns (uint256 tvl) {
    PositionBP memory positionInfo = registry.getPositionBP(vaultId, p.positionId);
    uint256 tokenId = abi.decode(p.data, (uint256));
    (address token0, address token1) = abi.decode(positionInfo.data, (address, address));
    uint256 amount0;
    uint256 amount1;
    (int24 tL, int24 tU, uint24 fee) = abi.decode(p.additionalData, (int24, int24, uint24));
    {
        IUniswapV3Pool pool = IUniswapV3Pool(factory.getPool(token0, token1, fee));
        bytes32 key = keccak256(abi.encodePacked(positionManager, tL, tU));

        (uint128 liquidity,,, uint128 tokensOwed0, uint128 tokensOwed1) = pool.positions(key);

        (uint160 sqrtPriceX96,,,,,,) = pool.slot0();
        (amount0, amount1) = LiquidityAmounts.getAmountsForLiquidity(
            sqrtPriceX96, TickMath.getSqrtRatioAtTick(tL), TickMath.getSqrtRatioAtTick(tU), liquidity
        );
        amount0 += tokensOwed0;
        amount1 += tokensOwed1;
    }

    tvl += valueOracle.getValue(token0, base, amount0);
    tvl += valueOracle.getValue(token1, base, amount1);
}
```
This assumption is incorrect as it presumes that all liquidity within the provided ticks is owned by Noya’s UniV3 Connector. This leads to wrong `TVL` calculation within the protocol, potentially inflating the TVL beyond its actual value. Consequently, this could undermine the protocol’s solvency by incorrectly inflating its perceived total assets.

## Recommendation
Use `positionsManager` `positions` getter instead to provide accurate liquidity owned by connector.

True, needs to be fixed. Not High severity though in my opinion.
