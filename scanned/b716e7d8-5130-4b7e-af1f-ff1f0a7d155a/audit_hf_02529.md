# [M] Loss of phoenix fee collections from initial liquidity

## Summary
Severity: Medium
Contest weight: 0.4176
Dataset id: 13526
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Minting.addLiquidityToInfernoPhoenixPool, it allows the admin to invoke a one-time initial liquidity addition of INITIAL_TITAN_X_FOR_LIQ to the INF/PHOENIX pool, with a subsequent position minted to the Minting contract. The fees obtained for contributing to the initial liquidity of the INF/PHOENIX pool can be collected via an admin only collectFees function. Notice how the obtained inferno is transferred to the fluxStakingVault to be staked, whereas the phoenix obtained is simply burned, essentially representing a loss of fees.
```solidity
function collectFees() external returns (uint256 amount0, uint256 amount1) {
    LP memory _lp = lp;
    INonfungiblePositionManager.CollectParams memory params = INonfungiblePositionManager.CollectParams({
        tokenId: _lp.tokenId,
        amount0Max: type(uint128).max,
        amount1Max: type(uint128).max
    });
    (amount0, amount1) = INonfungiblePositionManager(positionManager).collect(params);
    (uint256 phoenixAmount, uint256 infernoAmount) = _lp.isPhoenixToken0 ? (amount0, amount1) : (amount1, amount0);
    phoenix.burn(phoenixAmount);
}
```

## Recommendation
Consider a 50/50 split similar to the BuyAndBurn contract, where 50% is burned and 50% is transferred to the auctionTreasury to be auctioned off to provide fuel for the daily auctions which in turn provides value back to the buy&bid / buy&burn.
