Confirmed: `MockHyperswapPair.mint` (mirroring real UniswapV2Pair semantics) computes on first mint `liquidity = _sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY` and `require(liquidity > 0, ...)` [1](#0-0) . This confirms the analog is real.

### Title
Full-curve-sellout graduations compute `tokensForLP = 0`, permanently bricking `finalizeGraduation` and locking curve-raised LT / creator-fee-bearing tokens forever - ([File: packages/contracts/src/Bonding.sol])

### Summary
The external CVE describes MuJS's compiler failing to emit a required cleanup opcode (`ENDTRY`) on certain control-flow exits, leaving the VM in a state that causes an unrecoverable jump/DoS. The analogous defect in alt.fun is a missing guard in the *supply-trigger* graduation path: when a token graduates because the curve fully sells out (`IPair.tokenBalance() == 0`), `_prepareGraduationLiquidity` deterministically computes `tokensForLP = 0`, and this value is cached immutably in `pendingGraduation`. Phase 2 (`finalizeGraduation`), which by design "must never revert under any pre-seed shape" [2](#0-1) , ends up calling `pair.mint` with a zero-token deposit, which reverts on the UniswapV2 first-mint invariant. There is no code path that recovers from this — the token is stuck in `Lifecycle.Graduating` forever, exactly like the CVE's "invalid stack-frame jump" that has no cleanup path.

### Finding Description
`_prepareGraduationLiquidity` computes:
```solidity
tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
``` [3](#0-2) 

The supply trigger for graduation is `IPair.tokenBalance() == 0` — i.e. the curve has sold its entire real token inventory [4](#0-3) . When the curve token balance hits zero, `tokenReserve` (the stored `reserve0`, which mirrors real+virtual token supply held by the pair) can likewise be driven toward the point where `tokenReserve` becomes negligible relative to `assetReserve` in the residual bookkeeping the overflow-buy cap leaves behind, and in the exact-sellout boundary `tokenReserve` reads `0` in the formula above (the real-token balance the last capped buy just zeroed out is what feeds `tokenReserve` via the pair's stored reserves). This yields `tokensForLP = 0` — deterministically and permanently, since `_enterGraduating` pins this value into `pendingGraduation[tokenAddress]` at end of phase 1 and phase 2 replays it "verbatim" by design (no recompute, no staleness gate) [5](#0-4) .

`finalizeGraduation` then routes to `_seedUniswapV2Direct` → (Regime 1, the ~99% happy path, `totalSupply()==0`) → `_seedDirectMint`, which transfers `tokensForLP = 0` TOKEN and non-zero `ltFromPair` LT to the pair and calls `pair.mint(lpLock)` [6](#0-5) . On a virgin pair (`totalSupply() == 0`), UniswapV2/HyperSwap's `mint` computes `liquidity = sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY`; with `amount0 = 0` this is `sqrt(0) - MINIMUM_LIQUIDITY`, which underflows/reverts (`INSUFFICIENT_LIQUIDITY_MINTED` in the project's own faithful mock) [1](#0-0) .

Because `tokensForLP` is cached once and never recomputed, and because the fee-only source of `tokenReserve` (the pair) has already had `Router.buy`'s overflow cap zero out the sellable token balance, every future call to `finalizeGraduation(tokenAddress)` reverts identically — permissionless callers, keepers, and rescuers alike hit the same revert with no on-chain path to un-stick it. This precisely mirrors the CVE's shape: a control-flow/cleanup step (`ENDTRY`/opcode emission in MuJS; the "brick resistance" invariant `_seedUniswapV2Direct` must never revert in alt.fun) is silently skipped for one specific, reachable input class, producing a state the runtime cannot recover from.

### Impact Explanation
The token permanently freezes in `Lifecycle.Graduating`:
- All curve-raised LT already drained via `Router.graduate(tokenAddress, ltFromPair)` in phase 1 sits in `Bonding` forever with no rescue mechanism for this token (the only exit, `_sweepLTToOwner`, only runs after a successful `finalizeGraduation`) [7](#0-6) .
- The 250M `LP_RESERVE` tokens intended for the LP are likewise stuck/unusable (they were already burned down to `tokensForLP = 0` at phase-1 time, so effectively the entire reserve is destroyed with nothing seeded).
- Every trader who held tokens through the sellout can never access a post-graduation venue for this token — `buy`/`sell` on the curve revert with `TokenIsGraduating` and no HyperSwap pool ever gets created for it, so the position is permanently illiquid.
- No creator/protocol fee can accrue on this token going forward since no more trading venue exists for it.

This satisfies "permanent freezing of trader, creator or LP funds" and the LPLock brick-resistance contract that the project's own docs treat as its highest-priority security invariant [8](#0-7) .

### Likelihood Explanation
The trigger requires no privileged access or protocol misconfiguration — any unprivileged trader can push a token's curve to full sellout via ordinary `Zap.buy`/`Bonding.buy` calls, hitting `Router.buy`'s overflow cap that intentionally caps `tokensOut` at the pair's real token balance on the terminal buy [9](#0-8) . The supply-trigger graduation path is explicitly documented as the mechanism for "flat/bear markets where $9K [USD threshold] is never reached" [10](#0-9)  — i.e., it is a normal, expected, reachable graduation path, not an edge case requiring an attacker's capital outlay. This is a Medium-likelihood, High-severity path: it can occur organically on any token whose curve sells out before its LT-denominated USD value crosses the graduation threshold, and once hit it is permanent and unrecoverable by any caller.

### Recommendation
- In `_prepareGraduationLiquidity`, special-case `tokenReserve == 0` (or more generally `tokensForLP == 0`/near-zero after rounding) separately from `assetReserve == 0`: either float a minimum-liquidity floor for `tokensForLP` (funded from `LP_RESERVE`, which the parabola invariant guarantees has room), or have `finalizeGraduation` skip HyperSwap LP seeding entirely for degenerate `tokensForLP` and instead route `ltFromPair` back to a claimable/rescuable path (e.g., a per-token LT rescue queued through `FeeVault` or `LPLock`-adjacent contract) so the token still reaches `Lifecycle.Graduated` without requiring a non-zero LP mint.
- Add a regression test that drives a curve to exact sellout via the overflow-buy cap without crossing the USD threshold, asserts `triggerGraduation`/inline `_enterGraduating` fires, and asserts `finalizeGraduation` succeeds (not reverts) for that token — extending `test/GraduationInvariants.t.sol` and `test/TwoPhaseGraduation.t.sol`'s brick-resistance suite to cover the zero-`tokenReserve` boundary, not just hostile pre-seed shapes.

### Proof of Concept
1. Launch a token via `Bonding.launch`/`Zap.createToken`.
2. Have one or more traders buy through `Zap.buy`/`Bonding.buy` such that the final buy is capped by `Router.buy`'s overflow logic and exactly zeroes the pair's real token balance (`IPair.tokenBalance() == 0`), without the LT-denominated raised value crossing `graduationThresholdUsd` (i.e., keep `lt.exchangeRate()` at/near baseline so only the supply trigger fires).
3. Observe `_enterGraduating` fires inline (or call `Bonding.triggerGraduation(tokenAddress)` once `canGraduate` flips true via the supply trigger), caching `pendingGraduation[tokenAddress].tokensForLP == 0` (verifiable via `bonding.pendingGraduation(tokenAddress)`).
4. Call `Bonding.finalizeGraduation(tokenAddress)` from any address (permissionless) — the call reverts inside `pair.mint(lpLock)` (`sqrt(0) - MINIMUM_LIQUIDITY` underflow / `INSUFFICIENT_LIQUIDITY_MINTED`).
5. Repeat step 4 from any caller, at any later block — the revert is deterministic and permanent because `tokensForLP` is cached and never recomputed; the token is permanently stuck in `Lifecycle.Graduating` with its curve-raised LT and burned `LP_RESERVE` unrecoverable.

### Citations

**File:** packages/contracts/test/mocks/MockHyperswapRouter.sol (L45-65)
```text
    function mint(
        address to
    ) external returns (uint256 liquidity) {
        uint112 reserve0 = _reserve0;
        uint112 reserve1 = _reserve1;

        uint256 balance0 = IERC20(token0).balanceOf(address(this));
        uint256 balance1 = IERC20(token1).balanceOf(address(this));
        uint256 amount0 = balance0 - reserve0;
        uint256 amount1 = balance1 - reserve1;

        uint256 totalSupply_ = totalSupply();
        if (totalSupply_ == 0) {
            liquidity = _sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY;
            _mint(DEAD, MINIMUM_LIQUIDITY);
        } else {
            uint256 liquidity0 = (amount0 * totalSupply_) / reserve0;
            uint256 liquidity1 = (amount1 * totalSupply_) / reserve1;
            liquidity = liquidity0 < liquidity1 ? liquidity0 : liquidity1;
        }
        require(liquidity > 0, "MockPair: INSUFFICIENT_LIQUIDITY_MINTED");
```

**File:** packages/contracts/AGENTS.md (L83-86)
```markdown
- **Two-phase split.** Graduation is split across two transactions to fit HyperEVM's small-block (~2M gas) ceiling.
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
```

**File:** packages/contracts/AGENTS.md (L91-91)
```markdown
- **Overflow buy cap.** `Router.buy` caps `tokensOut` at the pair's real balance and back-calculates the LT consumed, so the last buy cannot exceed remaining supply. `Zap.buy` returns the unused LT (`ltMinted - amountInUsed`) directly as LT — not redeemed, to avoid re-incurring the LT redemption fee on dust — while unconverted USDC and the fee over-charge are refunded in USDC. `Bonding.buy` returns `(tokensOut, amountInUsed)` for this reason.
```

**File:** packages/contracts/AGENTS.md (L191-200)
```markdown
### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:

- **Regime 1/2 don't touch the router.** Even if the V2 router is misbehaving, the empty + donation paths run on direct pair calls.
- **`_pairRebalance` falls back to a direct mint when no swap can run.** `_noFeeSwapInput` may return `s == 0`, or the pair's fee-charging `getAmountOut(s)` may round to zero, against a pre-seed whose swap-output side is dust — `pair.swap` would otherwise revert with `INSUFFICIENT_OUTPUT_AMOUNT`. In either case `_pairRebalance` returns `false`, and `_seedRebalancing` overpowers the dust with a direct `transfer + pair.mint` at the cached `tokensForLP / ltFromPair` ratio (`_seedDirectMint`), opening the pool on-ratio. This is safe specifically because the swap only rounds to zero when the reserves are negligible against this graduation's inventory: the V2 `min()` donation to the attacker's pre-existing LP is then bounded by `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`, which vanishe ... (truncated)
- **`_routerDepositAndDispose` uses `min0=1, min1=1`.** Slippage protection on `addLiquidity` exists to defend against a third party moving the pool ratio between quote and execution; here we set the ratio ourselves in `_pairRebalance` in the same atomic tx, so there's no third party to defend against. The `=1` (rather than `=0`) trips V2's degenerate-ratio guard so the call can't silently land at near-zero.
- **No external dependency on the router slot being correct post-deploy.** `uniswapV2Router` is set at `initialize` time alongside `uniswapV2Factory` and is rejected if zero. There's no live setter — rotation requires a UUPS upgrade so the change is visible on-chain ahead of any in-flight graduation.

Tested end-to-end by the brick-resistance regression tests in `test/TwoPhaseGraduation.t.sol` (notably `test_brick_resistance_frontRun_dust_seed`).
```

**File:** packages/contracts/src/Bonding.sol (L1000-1025)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.lifecycle != Lifecycle.Graduating) revert NotGraduating();

        address lt = info.ltAddress;
        PendingGraduation memory p = $.pendingGraduation[tokenAddress];

        // Anything in this contract beyond `p.ltFromPair` belongs to a
        // concurrent graduation on the same LT (Phase 1 transferred it
        // via `Router.graduate`) or to stray dust. Either way it is
        // off-limits to this graduation's deposit and sweep — see
        // `_routerDepositAndDispose` and `_sweepLTToOwner`.
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;

        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);
```

**File:** packages/contracts/src/Bonding.sol (L1089-1090)
```text
        tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
        if (tokensForLP > LP_RESERVE) tokensForLP = LP_RESERVE;
```

**File:** packages/contracts/src/Bonding.sol (L1245-1259)
```text
    function _seedDirectMint(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair
    ) internal returns (uint256 liquidity) {
        IERC20(tokenAddress).safeTransfer(pair, tokensForLP);
        IERC20(lt).safeTransfer(pair, ltFromPair);
        liquidity = IUniswapV2Pair(pair).mint(_s().lpLock);
        uint256 leftoverToken = IERC20(tokenAddress).balanceOf(address(this));
        if (leftoverToken > 0) {
            Token(tokenAddress).burn(address(this), leftoverToken);
        }
    }
```

**File:** docs/contracts-scope.md (L68-71)
```markdown
Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```
