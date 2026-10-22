# [H] Potential Front-Running For Migration Blocking

## Summary
Severity: High
Contest weight: 0.7862
Dataset id: 13113
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SushiSwap has developed unique tokenomics in two phases: In the first phase, traders stake the UniswapV2's liquidity pools tokens for mining SUSHI tokens; and in the second phase, traders are meant to migrate those UniswapV2's liquidity pools tokens for the underlying assets to the SushiSwap DEX. The migration might be incentivized by the different token distribution mechanics proposed by SushiSwap. Specifically, with the current UniswapV2 configuration, 0.3% of all trading fees in any pool are proportionately distributed to the pool's liquidity providers. In comparison, SushiSwap allocates 0.25% directly to the active liquidity providers, but the remaining 0.05% are converted back to SUSHI and re-distributed to the SUSHI token holders.

Figure 3.1: The Migration Procedure

Mechanically, the migration procedure can be divided into four distinct steps: deploy sushiFactory, deploy migrator, configure MasterChef, and start migration. Note these four steps need to be sequentially executed and the timing of their execution is crucial. In particular, if we examine the final step, i.e., start migration, the migration process is kicked off by invoking the migrate() routine, which has a final check in place after the migration, i.e., require(bal == newLpToken.balanceOf(address(this)), "migrate: bad"). For simplicity, we call this particular check as the migration check.

```solidity
function migrate(uint256 _pid) public {
    require(address(migrator) != address(0), "migrate: no migrator");
    PoolInfo storage pool = poolInfo[_pid];
    IERC20 lpToken = pool.lpToken;
    uint256 bal = lpToken.balanceOf(address(this));
    lpToken.safeApprove(address(migrator), bal);
    IERC20 newLpToken = migrator.migrate(lpToken);
    require(bal == newLpToken.balanceOf(address(this)), "migrate: bad");
    pool.lpToken = newLpToken;
}
```

The actual bulk work of migration is performed by the Migrator contract in a function also named migrate() (we show the related code snippet below). It in essence burns the UniswapV2's liquidity pool (or LP) tokens to reclaim the underlying assets and transfers them to SushiSwap for minting of the corresponding new pair's LP tokens.

```solidity
function migrate(IUniswapV2Pair orig) public returns (IUniswapV2Pair) {
    require(msg.sender == chef, "not from master chef");
    require(block.number >= notBeforeBlock, "too early to migrate");
    require(orig.factory() == oldFactory, "not from old factory");
    address token0 = orig.token0();
    address token1 = orig.token1();
    IUniswapV2Pair pair = IUniswapV2Pair(factory.getPair(token0, token1));
    if (pair == IUniswapV2Pair(address(0))) {
        pair = IUniswapV2Pair(factory.createPair(token0, token1));
    }
    uint256 lp = orig.balanceOf(msg.sender);
    if (lp == 0) return pair;
    desiredLiquidity = lp;
    orig.transferFrom(msg.sender, address(orig), lp);
    orig.burn(address(pair));
    pair.mint(msg.sender);
    desiredLiquidity = uint256(*1);
    return pair;
}
```

We emphasize that the staked UniswapV2's LP tokens are transferred back to the UniswapV2 pair for redemption of the underlying assets (lines 39*40) and the redeemed underlying assets are then sent to the new pair in SushiSwap for minting (lines 40*41).

The new SushiSwap pair's mint() function is shown below. Here comes the critical part: the migration process assumes the migrator is the first to mint the new LP tokens (of this particular trading pair). Otherwise, the migration will fail! This assumption essentially reflects the code logic in lines 126*128. In other words, if an actor is able to front-run it to become the first one in successfully minting the new LP tokens, the actor will successfully block this migration (of this specific trading pair or the pool in MasterChef).

```solidity
function mint(address to) external lock returns (uint liquidity) {
    (uint112 _reserve0, uint112 _reserve1,) = getReserves(); // gas savings
    uint balance0 = IERC20Uniswap(token0).balanceOf(address(this));
    uint balance1 = IERC20Uniswap(token1).balanceOf(address(this));
    uint amount0 = balance0.sub(_reserve0);
    uint amount1 = balance1.sub(_reserve1);
    bool feeOn = _mintFee(_reserve0, _reserve1);
    uint _totalSupply = totalSupply; // gas savings, must be defined here since totalSupply can update _mintFee
    if (_totalSupply == 0) {
        address migrator = IUniswapV2Factory(factory).migrator();
        if (msg.sender == migrator) {
            liquidity = IMigrator(migrator).desiredLiquidity();
            require(liquidity > 0 && liquidity != uint256(*1), "Bad desired liquidity");
        } else {
            require(migrator == address(0), "Must not have migrator");
        }
        liquidity = Math.sqrt(amount0.mul(amount1)).sub(MINIMUM_LIQUIDITY);
        _mint(address(0), MINIMUM_LIQUIDITY); // permanently lock the first MINIMUM_LIQUIDITY tokens
    } else {
        liquidity = Math.min(
            amount0.mul(_totalSupply) / _reserve0,
            amount1.mul(_totalSupply) / _reserve1
        );
    }
    require(liquidity > 0, "UniswapV2: INSUFFICIENT_LIQUIDITY_MINTED");
    _mint(to, liquidity);
    _update(balance0, balance1, _reserve0, _reserve1);
    if (feeOn) kLast = uint(reserve0).mul(reserve1); // reserve0 and reserve1 are up-to-date
    emit Mint(msg.sender, amount0, amount1);
}
```

Recall the above migration check that essentially states the new LP token amount should equal to the old LP token amount. If the migration transaction is not the first to mint new LP tokens, the first transaction that successfully mints the new LP tokens will lead to _totalSupply != 0. In other words, the migration transaction will be forced to take the execution path in lines 135, not the intended lines 126*128. As a result, the minted amount is unlikely to be the same as the old UniswapV2's pool token amount before migration, hence failing the migration check! To ensure a smooth migration process, we need to guarantee the first minting of new LP tokens is launched by the migration transaction. To achieve that, we need to prevent any unintended minting (of new LP tokens) between the first step deploy sushiFactory and the third step configure MasterChef. A natural approach is to complete the initial three steps within the same transaction, best facilitated by a contract-coordinated deployment.

## Recommendation
Deploy these contracts in a coherent fashion and avoid the above-mentioned front-running to guarantee a smooth migration.
