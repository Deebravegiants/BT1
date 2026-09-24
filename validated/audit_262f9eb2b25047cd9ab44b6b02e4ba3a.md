Confirmed: `Pair.swap` updates `_pool.assetReserve` by the caller-supplied `assetIn`/`assetOut` deltas, never by reading `IERC20(assetToken).balanceOf(address(this))` before/after the transfer [1](#0-0) . `Router.buy` computes `amountInUsed` from the constant-product formula, then calls `IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed)` followed by `pair.swap(0, tokensOut, amountInUsed, 0)`, which books the full `amountInUsed` into `assetReserve` regardless of what the pair actually received [2](#0-1) . `Router.sell` has the same pattern: it transfers `token` in, computes `assetOut` from stored reserves, and calls `pair.swap(amountIn, 0, 0, assetOut)` [3](#0-2) .

### Title
Bookkeeping assumes the LT reserve asset is a non-fee-on-transfer / non-rebasing-on-transfer token, letting `assetReserve` desync from `Pair`'s real LT balance - ([File: packages/contracts/src/Router.sol, packages/contracts/src/Pair.sol])

### Summary
The bug class from the external report — an off-chain/bookkeeping system trusting the *requested* transfer amount instead of the *actually received* balance delta when the reserve token is deflationary/inflationary/fee-on-transfer — maps directly onto how `Router`/`Pair` account for the LT reserve on every buy and sell. `Pair.swap` never reads live `balanceOf`; it advances `_pool.assetReserve`/`_pool.tokenReserve` purely from the deltas passed in by `Router`, and `Router.buy`/`Router.sell` compute those deltas from the AMM math, not from the LT's actual transfer outcome.

### Finding Description
`Pair.swap(tokenIn, tokenOut, assetIn, assetOut)` is a pure ledger update: `newAssetReserve = (_pool.assetReserve + assetIn) - assetOut`, with no `balanceOf` reconciliation [1](#0-0) . `Router.buy` transfers `amountInUsed` of the LT (`asset`) into the pair via `safeTransferFrom`, then unconditionally books `assetIn = amountInUsed` in the same call [4](#0-3) . If BounceTech's `mint`/transfer flow, or the LT itself, were to deduct any fee/streaming-fee-on-transfer, rebase down mid-transfer, or otherwise deliver less than `amountInUsed` to the pair, `_pool.assetReserve` would be inflated relative to the pair's real LT balance (`IERC20(assetToken).balanceOf(pair)`). Every subsequent quote (`_computeBuy`/`_computeSell`, both driven by `getReserves()`/`k()`, not live balance) is then computed against a phantom reserve, and the graduation math (`_prepareGraduationLiquidity`, which reads `getReserves()` directly, not `assetBalance()`) would drain/seed the LP against a reserve figure the pair does not actually hold [5](#0-4) . The protocol's own documentation shows it is aware of, and defends against, one specific direction of this class (donations inflating live `balanceOf` reads for graduation triggers) by switching those checks to stored reserves rather than `balanceOf` [6](#0-5)  — but this "trust the stored ledger" design is exactly what breaks in the *opposite* direction if the reserve asset ever short-transfers what `Router` believes it sent, since nothing reconciles `_pool.assetReserve` against `Pair.assetBalance()` after a swap.

### Impact Explanation
If the LT reserve asset ever behaves as fee-on-transfer or under-delivers relative to the requested transfer amount, the pair's internal `k`-based accounting permanently diverges from its real LT holdings. This can freeze trading (K-invariant checks in `_computeSell`/`_computeBuy` and `Pair.swap`'s `(newReserveX+1)*(newReserveY+1) < k` guard start reverting against a balance the pair no longer has) or, at graduation, cause `_prepareGraduationLiquidity`/`Router.graduate` to attempt to move `ltFromPair` LT out of the pair that the pair doesn't actually hold, reverting `finalizeGraduation` and permanently freezing curve funds and the LP seeding for that token [5](#0-4) .

### Likelihood Explanation
Currently low/unproven against the specific BounceTech LT deployed today — the codebase's own `MockLeveragedToken.mint`/`redeem` are simple 1:1 non-fee transfers [7](#0-6) , and I could not locate the live BounceTech `LeveragedToken` source in this index to confirm whether its `transfer` path can ever deduct a fee (the docs describe an accruing "streaming fee" realized only via `mint`/`redeem`/checkpoint, not a transfer-time fee) [8](#0-7) . The root cause — `Pair.swap` trusting caller-supplied deltas with no balance reconciliation — is real and reachable by any unprivileged buyer/seller (`Zap.buy`/`Zap.sell` → `Bonding.buy`/`sell` → `Router.buy`/`sell` → `Pair.swap`), but exploitability depends entirely on the external LT's transfer semantics, which this report's own rules (analogs must stand on alt.fun's code, not the external LT) limit how far I can push without access to BounceTech's live contract.

### Recommendation
- **Short term**: Document explicitly (as the report recommends) that the bridge/AMM's bookkeeping assumes the LT is not fee-on-transfer and does not deduct value on `transfer`/`transferFrom`; add this as an integration precondition for any future reserve-asset LT.
- **Long term**: Have `Router.buy`/`Router.sell` measure the pair's actual `assetToken`/`launchedToken` balance delta (before/after `safeTransferFrom`) rather than trusting the pre-computed `amountInUsed`, and pass that measured delta into `Pair.swap`, so `_pool.assetReserve`/`tokenReserve` can never diverge from real holdings regardless of the reserve token's transfer behavior.

### Proof of Concept
Conceptual (cannot be fully instantiated against the real BounceTech LT from this index):
1. `trader` calls `Zap.buy(tokenAddress, usdcAmount, 0, ref)` → mints LT → `Bonding.buy` → `Router.buy(amountIn, token, zap)`.
2. `Router.buy` computes `amountInUsed` via `_computeBuy` and calls `IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed)` [9](#0-8) .
3. If the LT deducts any fee on this transfer (hypothetically `f` bps), `pairAddr` actually receives `amountInUsed*(1-f)` LT.
4. `Router.buy` still calls `pair.swap(0, tokensOut, amountInUsed, 0)`, booking the full pre-fee `amountInUsed` into `_pool.assetReserve` [1](#0-0) .
5. `_pool.assetReserve` now exceeds `IERC20(assetToken).balanceOf(pairAddr)` by `amountInUsed*f`. Every later `_computeBuy`/`_computeSell` and `_prepareGraduationLiquidity`'s `ltFromPair = assetReserve - virtualLtReserve` computation is now based on a reserve figure larger than what the pair can actually deliver, and `Router.graduate`'s `transferAsset(msg.sender, ltFromPair)` (a plain `safeTransfer`) will revert or under-fund the LP once the shortfall accumulates enough to exceed the pair's true LT balance [10](#0-9) .

### Citations

**File:** packages/contracts/src/Pair.sol (L65-79)
```text
    function swap(
        uint256 tokenIn,
        uint256 tokenOut,
        uint256 assetIn,
        uint256 assetOut
    ) external onlyRouter returns (bool) {
        uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
        uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
        if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();

        _pool.tokenReserve = newTokenReserve;
        _pool.assetReserve = newAssetReserve;
        emit Swap(tokenIn, tokenOut, assetIn, assetOut);
        return true;
    }
```

**File:** packages/contracts/src/Router.sol (L92-108)
```text
    function buy(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 amountInUsed, uint256 tokensOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);

        (amountInUsed, tokensOut) = _computeBuy(pairAddr, amountIn);

        IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed);

        IPair(pairAddr).transferToken(to, tokensOut);
        IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0);
    }
```

**File:** packages/contracts/src/Router.sol (L151-170)
```text
    function sell(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 tokensIn, uint256 assetOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        tokensIn = amountIn;

        IERC20(token).safeTransferFrom(to, pairAddr, amountIn);

        assetOut = _computeSell(pairAddr, amountIn);

        IPair(pairAddr).transferAsset(to, assetOut);

        IPair(pairAddr).swap(amountIn, 0, 0, assetOut);
    }
```

**File:** packages/contracts/src/Router.sol (L203-211)
```text
    function graduate(
        address token,
        uint256 amount
    ) external onlyRole(BONDING_ROLE) {
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        IPair(pairAddr).transferAsset(msg.sender, amount);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1073-1096)
```text
    function _prepareGraduationLiquidity(
        address tokenAddress
    ) internal returns (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) {
        address pairAddr = _s().tokenInfo[tokenAddress].pair;
        (uint256 tokenReserve, uint256 assetReserve) = IPair(pairAddr).getReserves();

        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
            Token(tokenAddress).burn(pairAddr, unsoldBurned);
        }

        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }

        tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
        if (tokensForLP > LP_RESERVE) tokensForLP = LP_RESERVE;

        lpBurned = LP_RESERVE - tokensForLP;
        if (lpBurned > 0) {
            Token(tokenAddress).burn(address(this), lpBurned);
        }
    }
```

**File:** docs/contracts-scope.md (L70-71)
```markdown
- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```

**File:** docs/contracts-scope.md (L75-75)
```markdown
**Exchange-rate freshness on the USD trigger.** The USD trigger reads the LT's `exchangeRate()`, a view that reports `totalAssets / totalSupply` *without* settling the LT's accrued streaming fee — that fee is only realised when a `mint` / `redeem` / agent checkpoint runs on the LT. The view therefore sits marginally above the post-checkpoint rate, by at most the pending fee (`≈ streamingFee × leverage × time-since-last-checkpoint`; sub-cent for the actively-traded LTs supported here). The effect is benign and one-directional: a token can enter `Graduating` a touch before its settled reserve value crosses the threshold. The threshold-crossing buy path is unaffected — every buy mints LT and `mint` checkpoints the LT in the same tx, so `canGraduate` reads a freshly-settled rate there; only th ... (truncated)
```

**File:** packages/contracts/test/mocks/MockLeveragedToken.sol (L41-65)
```text
    function mint(
        address to,
        uint256 baseAmount,
        uint256
    ) external returns (uint256 ltAmount) {
        if (_minTransactionSize > 0 && baseAmount < _minTransactionSize) {
            revert BelowMinTransactionSize();
        }
        ERC20(baseAsset).transferFrom(msg.sender, address(this), baseAmount);
        ltAmount = baseToLtAmount(baseAmount);
        _mint(to, ltAmount);
    }

    function redeem(
        address to,
        uint256 ltAmount,
        uint256
    ) external returns (uint256 baseAmount) {
        _burn(msg.sender, ltAmount);
        baseAmount = ltToBaseAmount(ltAmount);
        if (_minTransactionSize > 0 && baseAmount < _minTransactionSize) {
            revert BelowMinTransactionSize();
        }
        ERC20(baseAsset).transfer(to, baseAmount);
    }
```
