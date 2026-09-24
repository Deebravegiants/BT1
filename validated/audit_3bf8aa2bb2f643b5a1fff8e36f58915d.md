### Title
Missing on-chain incentive for permissionless `finalizeGraduation` risks indefinite freezing of curve-raised LT and reserve tokens - (File: `packages/contracts/src/Bonding.sol`)

### Summary
Like the `CurrencyGovernance`/`PolicyVotes` pattern in the original report — where `commit`/`reveal`/`computeVote`/`execute` require an altruistic caller with no embedded on-chain reward — alt.fun's graduation flow requires a second, separate, gas-costly transaction (`finalizeGraduation`) to complete a state transition that has already begun (`triggerGraduation` / inline `_enterGraduating`). Nothing in the contract compensates the caller of `finalizeGraduation`; the system instead depends entirely on an off-chain, centralized "Cloudflare Worker keeper" to drive the happy path, exactly the centralization risk the original report flags.

### Finding Description
Graduation is deliberately split into two transactions because seeding the HyperSwap V2 LP exceeds HyperEVM's ~2M small-block gas ceiling [1](#0-0) . Phase 1 (`_enterGraduating`) fires inline on a threshold-crossing buy or via the permissionless `triggerGraduation`, draining the curve, caching LP amounts in `pendingGraduation[token]`, flipping `lifecycle` to `Graduating`, and **freezing all trading** for that token [2](#0-1) . While `Graduating`, both `buy` and `sell` unconditionally revert with `TokenIsGraduating` [3](#0-2) .

Completing the process requires someone to call `finalizeGraduation(tokenAddress)`, a ~2.5M-gas call that creates/seeds the HyperSwap pair, locks LP, and flips the token to `Graduated` [4](#0-3) . The function is explicitly permissionless and pays the caller nothing — no fee rebate, no bounty, no priority allocation. The protocol's own documentation states the design relies on an off-chain centralized keeper for the happy path, with permissionless calling only as a "rescue" fallback: *"A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token."* [5](#0-4) 

Between the two phases, all of the curve-raised LT (`ltFromPair`) and up to 250M reserve tokens (`LP_RESERVE`) sit parked inside `Bonding`, unusable by anyone, and every holder of that token is locked out of trading until `finalizeGraduation` lands [6](#0-5) . This is structurally identical to the original report's concern: functions essential to finishing a value-bearing on-chain process (`reveal`, `computeVote`, `execute` there; `finalizeGraduation` here) have no embedded incentive, so the protocol's continued liveness depends on a centralized entity (the Eco team there; the Cloudflare Worker keeper here) rather than a transparent, trustless mechanism baked into the contract.

### Impact Explanation
If the off-chain keeper is unavailable (downtime, censorship, key compromise, operator decommissioning it) and no altruistic third party steps in — because there is zero on-chain reward for doing so, only gas cost — every token stuck in `Graduating` remains untradeable indefinitely: holders cannot sell, buyers cannot buy, and the curve-raised LT plus 250M reserve tokens remain parked and idle in `Bonding`. This is a freezing-of-funds condition reachable purely by keeper inaction, with no in-protocol backstop compensating a rescuer for stepping in.

### Likelihood Explanation
Medium likelihood: the keeper is a single off-chain, centralized component outside the audited contract surface; any of its outages, RPC failures, or decommissioning directly creates the stuck-token condition. Because calling `finalizeGraduation` costs real gas (~2.5M gas call) with strictly zero on-chain reward, rational actors have no financial reason to call it once the keeper stops, so reliance on "someone eventually cares enough" mirrors exactly the pattern the original report calls out as insufficiently robust.

### Recommendation
Add an on-chain incentive for `finalizeGraduation` (and `triggerGraduation`) callers, e.g., a small bounty carved out of the LT parked in `Bonding` during Phase 1, or priority/rebate against the protocol fee stream, paid atomically to `msg.sender` on successful finalize. At minimum, document the centralized-keeper dependency and its risk explicitly in the contract's NatSpec (beyond internal `AGENTS.md`), consistent with the Eco team's stated remediation of compensating callers conditional on completing the action.

### Proof of Concept
1. A buy crosses the graduation threshold; `_enterGraduating` fires, `lifecycle` flips to `Graduating`, trading freezes (`test_phase1_buy_during_pending_reverts`, `test_phase1_sell_during_pending_reverts`) [3](#0-2) .
2. Assume the Cloudflare Worker keeper is down (outage/censorship/decommission).
3. No unprivileged actor has an on-chain financial reason to spend ~2.5M gas calling `finalizeGraduation`; the function pays the caller nothing (`function finalizeGraduation(address tokenAddress) external nonReentrant { ... }` — no reward path) [7](#0-6) .
4. The token remains permanently in `Lifecycle.Graduating`: holders can't sell (`TokenIsGraduating`), new buyers can't buy, and `ltFromPair` LT plus up to 250M reserve tokens stay parked in `Bonding`, exactly the fund-freezing risk the original report warns follows from uncompensated, essential finalize-style calls.

### Citations

**File:** packages/contracts/AGENTS.md (L83-86)
```markdown
- **Two-phase split.** Graduation is split across two transactions to fit HyperEVM's small-block (~2M gas) ceiling.
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
```

**File:** packages/contracts/AGENTS.md (L87-87)
```markdown
- **Virtual token reserve.** At launch, `Pair.reserve0 = totalSupply (1B)` while only `curveSupply = 75%` (750M) of real tokens are transferred to the pair. The other 250M (`LP_RESERVE`) sit in `Bonding` for graduation. This extends the curve beyond the sellable supply, which is what makes dynamic LP seeding work cleanly.
```

**File:** packages/contracts/src/Bonding.sol (L938-953)
```text
    function _enterGraduating(
        address tokenAddress
    ) internal {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        info.lifecycle = Lifecycle.Graduating;

        (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) =
            _prepareGraduationLiquidity(tokenAddress);

        $.pendingGraduation[tokenAddress] = PendingGraduation({
            tokensForLP: tokensForLP, ltFromPair: ltFromPair, lpBurned: lpBurned, unsoldBurned: unsoldBurned
        });

        emit TokenGraduating(tokenAddress, tokensForLP, ltFromPair, lpBurned, unsoldBurned);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1000-1034)
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

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
    }
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L122-152)
```text
    function test_phase1_buy_during_pending_reverts() public {
        (address tokenAddr,) = _launchToken();
        _enterGraduating(tokenAddr);

        uint256 attempt = _ltGraduationTrigger();
        lt.mintDirect(trader, attempt);
        vm.startPrank(trader);
        lt.approve(address(curveRouter), attempt);
        vm.expectRevert(Bonding.TokenIsGraduating.selector);
        bonding.buy(attempt, tokenAddr, 0, trader);
        vm.stopPrank();
    }

    function test_phase1_sell_during_pending_reverts() public {
        // Seed a holder before graduating so they have something to try to sell.
        (address tokenAddr,) = _launchToken();
        _buyNoFinalize(tokenAddr, trader, _ltStageBeforeGraduation());
        uint256 holderBalance = Token(tokenAddr).balanceOf(trader);
        assertTrue(holderBalance > 0);

        // Now graduate via the standard rate-pump pattern.
        lt.setExchangeRate(_ratePumpForStagedGraduation());
        _buyNoFinalize(tokenAddr, trader2, _ltGraduationTrigger());
        assertTrue(bonding.isGraduating(tokenAddr));

        vm.startPrank(trader);
        Token(tokenAddr).approve(address(curveRouter), holderBalance);
        vm.expectRevert(Bonding.TokenIsGraduating.selector);
        bonding.sell(holderBalance, tokenAddr, 0, trader);
        vm.stopPrank();
    }
```
