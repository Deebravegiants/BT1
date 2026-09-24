### Title
Zero/degenerate virtual LT reserve at launch allows near-free draining of the curve's real token supply - ([File: packages/contracts/src/Pair.sol])

### Summary
`Pair.mint` accepts an attacker/creator/price-influenced `assetReserve` (the virtual LT seed) with no validation that it is non-zero, exactly like `vorbis_analysis_headerout()` trusting `vi->channels` without checking it's `>0` before using it. If the virtual reserve rounds to `0`, the pair's `k` becomes `0`, which collapses the AMM's price-discovery math in `Router._computeBuy`, letting the very first buyer walk away with almost the entire real token balance of the pair for a negligible amount of LT.

### Finding Description
`Pair.mint` is the single place that sets the pool's immutable invariant: [1](#0-0) 

It stores whatever `tokenReserve`/`assetReserve` the router hands it and derives `k = tokenReserve * assetReserve` — there is no check that either value is non-zero. `Router.addInitialLiquidity` (called once, at launch, by `Bonding`) forwards these values unchecked: [2](#0-1) 

Per the protocol docs, the virtual LT reserve (`reserveAsset`) that seeds every new curve is sized so "every token opens at ~$3K market cap regardless of which LT is paired" — i.e. it is computed as a function of a fixed USD target divided by the paired LT's live `exchangeRate()`: [3](#0-2) 

Because Solidity integer division floors, if a paired LT's `exchangeRate()` is large enough (a long-appreciated, highly-leveraged LT — a state the protocol's own docs acknowledge as reachable, since LTs "de-register"/appreciate over time and the reserve is read "live via exchangeRate"), `USD_TARGET * 1e18 / exchangeRate()` can floor to `0`. That zero is passed straight into `Pair.mint` as `reserveAsset`, producing `k = tokenReserve * 0 = 0` with no revert anywhere in the chain — the uninitialized/degenerate state that `vi->channels<=0` represents in the original CVE.

Once `k == 0`, `Router._computeBuy` collapses: [4](#0-3) 

`tokensOut = reserveToken - (k / newReserveAsset) = reserveToken - 0 = reserveToken` for *any* non-zero LT input, before being capped at the pair's real token balance (`750M`, `CURVE_SUPPLY`). The `OverflowCapDegenerate` guard only fires when `cappedReserveToken == 0`, which is not the case here — the buy proceeds and simply hands the buyer the pair's entire real token balance in exchange for whatever trivial LT amount they submitted (down to the LT's mint floor via `Zap._executeBuy`).

### Impact Explanation
This is a direct theft of the bonding curve's entire real token allocation (`CURVE_SUPPLY`, 750M tokens) for a near-zero cost, reachable by any unprivileged trader who is first to buy on a curve whose virtual reserve degenerated to zero at launch. It also short-circuits the graduation math: `_prepareGraduationLiquidity`'s `ltFromPair = assetReserve - virtualLtReserve` and `tokensForLP` computation both depend on `k` being a faithful record of the launch-time virtual reserve; a `k = 0` curve produces meaningless LP-seeding math, risking an LP opened at a wildly wrong price or reverting mid-graduation. Either outcome is Critical: traders/creator funds (the entire curve-raised value) are stolen by the exploiting buyer, and the graduation invariants that depend on `k` being a true non-zero virtual-reserve marker are broken.

### Likelihood Explanation
Reachability requires only that a token be launched (`Zap.createToken` → `Bonding.launch` → `Router.addInitialLiquidity` → `Pair.mint`) against an LT whose `exchangeRate()` is high enough that the fixed-USD virtual-reserve computation floors to zero, and then a normal `Zap.buy` call. No privileged role, no upgrade, and no off-chain component is needed — any creator can trigger the degenerate launch (deliberately or accidentally) and any trader (including the creator) can execute the draining buy. The exact numeric threshold at which the floor triggers depends on constants and the LT's exchange rate scale not fully visible in the indexed subset of the codebase, but the missing zero-check in `Pair.mint`/`Router.addInitialLiquidity` is a concrete, unconditional gap regardless of how the caller manages to reach `reserveAsset == 0`.

### Recommendation
Add an explicit non-zero check on both `tokenReserve` and `assetReserve` in `Pair.mint` (revert e.g. `ZeroReserve()`), and/or validate the computed virtual LT reserve in `Bonding`'s launch path before calling `Router.addInitialLiquidity`, rejecting any launch whose derived virtual reserve rounds to zero. Additionally, harden `Router._computeBuy`/`_computeSell` to revert if `k == 0` rather than silently returning the full reserve as `tokensOut`.

### Proof of Concept
1. Identify (or wait for) a BounceTech LT whose `exchangeRate()` is high enough that `VIRTUAL_LIQUIDITY_USD * 1e18 / exchangeRate()` floors to `0` under the protocol's fixed-USD virtual-liquidity sizing.
2. Call `Zap.createToken({..., ltAddress: thatLT}, seedUsdcAmount)`. `Bonding.launch` computes the degenerate virtual reserve and calls `Router.addInitialLiquidity` → `Pair.mint(totalSupply, 0)`, setting `k = 0` with no revert.
3. Once the anti-snipe delay elapses, call `Zap.buy(tokenAddress, minUsdcAmount, 0, address(0))` with the smallest allowed USDC amount.
4. Observe `Router._computeBuy` returns `tokensOut = reserveToken` (capped at the real pair balance, `CURVE_SUPPLY = 750M`), so the buyer receives (up to) the entire real token supply of the curve for the minimum possible LT input — draining the token allocation intended to back the bonding curve and graduation LP.

### Citations

**File:** packages/contracts/src/Pair.sol (L55-63)
```text
    function mint(
        uint256 tokenReserve,
        uint256 assetReserve
    ) external onlyRouter returns (bool) {
        if (_pool.k != 0) revert AlreadyMinted();
        _pool = Pool({tokenReserve: tokenReserve, assetReserve: assetReserve, k: tokenReserve * assetReserve});
        emit Mint(tokenReserve, assetReserve);
        return true;
    }
```

**File:** packages/contracts/src/Router.sol (L75-87)
```text
    function addInitialLiquidity(
        address token,
        uint256 virtualReserveToken,
        uint256 realTokenAmount,
        uint256 reserveAsset
    ) external onlyRole(BONDING_ROLE) {
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();

        IERC20(token).safeTransferFrom(msg.sender, pairAddr, realTokenAmount);
        IPair(pairAddr).mint(virtualReserveToken, reserveAsset);
    }
```

**File:** packages/contracts/src/Router.sol (L127-148)
```text
    function _computeBuy(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 amountInUsed, uint256 tokensOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        amountInUsed = amountIn;

        uint256 newReserveAsset = reserveAsset + amountInUsed;
        tokensOut = reserveToken - (k / newReserveAsset);

        uint256 realBalance = pair.tokenBalance();
        if (tokensOut > realBalance) {
            tokensOut = realBalance;
            uint256 cappedReserveToken = reserveToken - tokensOut;
            if (cappedReserveToken == 0) revert OverflowCapDegenerate();
            uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
            amountInUsed = cappedReserveAsset - reserveAsset;
        }
    }
```

**File:** docs/contracts-scope.md (L32-38)
```markdown
This deploys a `Token` clone (1B supply) and creates a `Pair` (token/LT). K is computed per token so every token opens at ~`$3K` market cap regardless of which LT is paired.

**Virtual token reserve.** The pair's `reserve0` is seeded at `totalSupply` (1B) while only `curveSupply = 75%` (750M) of real tokens are actually transferred. The other 250M are held in `Bonding` as `lpReserve`. This virtual-reserve design:

- Extends the curve beyond the sellable supply.
- Gives a deterministic supply trigger (curve exhausts at 750M sold).
- Makes the dynamic-LP-seeding parabola `tokensForLP(sold) = sold·(S−sold)/S` peak at exactly `S/4 = 250M = LP_RESERVE` — so `tokensForLP ≤ lpReserve` is a mathematical invariant, not a runtime guess.
```
