### Title
Attacker-seeded HyperSwap pair reserves can overflow `Math.mulDiv` in `_noFeeSwapInput`, permanently bricking `finalizeGraduation` and freezing curve-raised funds - ([File: packages/contracts/src/Bonding.sol])

### Summary
The multihash `CVE-2020-35909` class is "a function whose signature promises a clean error but instead panics on attacker-supplied/malformed input, DoS-ing the caller." The closest reachable analog in alt.fun is `Bonding._noFeeSwapInput`, invoked from `_pairRebalance` → `_seedRebalancing` → `_seedUniswapV2Direct` → `finalizeGraduation`. It performs `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` on values that are directly attacker-controlled by pre-seeding the permissionless HyperSwap V2 TOKEN/LT pair before graduation. If the product overflows `uint256`, `Math.mulDiv` reverts, and because `finalizeGraduation` has no retry/adjustment path around this call, the token's graduation becomes permanently unfinalizable, freezing all curve-raised LT and the 250M LP-bound tokens that phase 1 already parked on `Bonding`.

### Finding Description
`finalizeGraduation` (`packages/contracts/src/Bonding.sol:1000-1034`) is permissionless phase-2 graduation. When the HyperSwap V2 pair for `(token, lt)` already has non-zero `totalSupply()` (i.e., someone pre-minted LP into it), the flow enters `_seedRebalancing` (`packages/contracts/src/Bonding.sol:1279-1354`), which reads the pair's live `(r0, r1)` reserves — values fully under an attacker's control since the pair is created and can be freely `mint()`'d by anyone via `_ensureUniswapV2Pair` (`packages/contracts/src/Bonding.sol:1121-1130`) before the token even graduates.

`_seedRebalancing` calls `_pairRebalance`, which calls `_noFeeSwapInput`: [1](#0-0) 

The natspec on this function explicitly acknowledges the risk: [2](#0-1) 

`reserveIn`/`reserveOut` are the pair's live `uint112` reserves (attacker-seedable up to `type(uint112).max ≈ 5.19e33` on the TOKEN side, and up to whatever the external LT supports on the LT side — LT itself is out of scope, but the pair reserve slot is not). `targetN` (`ltFromPair`) and `targetD` (`tokensForLP`) are pinned at phase 1 by `_prepareGraduationLiquidity` (`packages/contracts/src/Bonding.sol:1073-1096`) and are immutable once `Lifecycle.Graduating` is entered. `reserveIn * reserveOut` is a checked Solidity multiplication that itself does not overflow at these magnitudes, but `Math.mulDiv(a, targetN, targetD)` computes the full 512-bit product `a * targetN` and reverts if the quotient does not fit back into 256 bits (OpenZeppelin's `Math.mulDiv` overflow guard). Because `tokensForLP` can be very small (it is `ltFromPair * tokenReserve / assetReserve`, and the USD graduation trigger can fire from LT-price appreciation alone with little or no token sold — see `canGraduate`, `packages/contracts/src/Bonding.sol:680-695`), the divisor `targetD` can be small while `reserveIn * reserveOut * targetN` is attacker-inflated, driving the quotient past `type(uint256).max`.

Once this reverts, every future call to `finalizeGraduation(tokenAddress)` reverts identically, because the inputs (`p.tokensForLP`, `p.ltFromPair`, and the attacker's now-permanent pair reserves) never change. There is no owner or router override to force a different graduation path once `Lifecycle.Graduating` is set — `finalizeGraduation` is the only exit from that state.

### Impact Explanation
A successful trigger permanently freezes:
- All curve-raised LT already pulled into `Bonding` via `Router.graduate` in `_prepareGraduationLiquidity` (`packages/contracts/src/Bonding.sol:1084-1087`), and
- The `tokensForLP` (up to `LP_RESERVE` = 250,000,000 tokens) that were minted/reserved for the LP and are stuck in `Bonding` since `Token.burn`/transfer to the pair never completes.

This matches the contest's explicit "permanent freezing of trader, creator or LP funds" impact bucket and the named attack surface "LP seeding into an attacker-influenceable HyperSwap V2 pair... including the `_seedRebalancing` / `_pairRebalance` / `_seedDirectMint` fallbacks." It is High severity: unrecoverable fund lock affecting an entire token's raised capital, triggerable by any unprivileged address pre-seeding a permissionless AMM pair.

### Likelihood Explanation
Reaching the vulnerable branch requires:
1. The attacker to create the HyperSwap V2 TOKEN/LT pair before graduation (permissionless, `IUniswapV2Factory.createPair` — anyone can call this for any two ERC20s), and mint LP into it with a self-funded, deliberately skewed reserve ratio (`totalSupply() != 0` routes into `_seedRebalancing` rather than the safe empty-pair path).
2. Reserve magnitudes and the cached `(tokensForLP, ltFromPair)` ratio to be extreme enough that `reserveIn * reserveOut * targetN` exceeds `type(uint256).max` when divided by `targetD`.

Item (1) is fully permissionless and requires only capital to acquire TOKEN (buyable on the curve, bounded by total token supply ~1e27) and LT (external, bounded by BounceTech's own supply — outside this contract's control, but not zero-cost to rule out). Item (2) is favored specifically for tokens whose graduation is triggered by LT price appreciation with `tokensForLP` rounding small, which the contract's own `canGraduate` USD-trigger logic permits. This is a moderate-likelihood, capital-gated griefing/DoS vector rather than a trivial one-click exploit, but the contract's own comments show the developers were aware an "adversarial input... would revert" and treated that as acceptable without providing any recovery path.

### Recommendation
- Bound `_noFeeSwapInput`'s inputs defensively before the `Math.mulDiv` call (e.g., cap `reserveIn`/`reserveOut` against a sane multiple of `targetN`/`targetD`, or perform the computation in a way that saturates instead of reverts), OR
- Wrap the rebalance computation in `_seedRebalancing` with a `try/catch`-equivalent (a low-level call, since `Math.mulDiv` isn't external) that falls back to `_seedDirectMint` — mirroring the existing brick-resistance pattern already used for the `INSUFFICIENT_OUTPUT_AMOUNT` case — whenever the rebalance math cannot be computed safely, so a hostile pre-seed can never permanently prevent `finalizeGraduation` from completing.
- Add an owner-gated emergency path to re-route a permanently stuck `Lifecycle.Graduating` token to a fallback seeding strategy that does not depend on `_noFeeSwapInput`.

### Proof of Concept
1. Attacker calls `IUniswapV2Factory(uniswapV2Factory).createPair(token, lt)` for a not-yet-graduated `token` (permissionless).
2. Attacker acquires a large amount of `token` (buying on the curve) and a large amount of `lt`, transfers both into the pair, and calls `pair.mint(attacker)`, setting `(r0, r1)` to a heavily skewed, near-`uint112`-max ratio.
3. Attacker (or LT price drift) causes `canGraduate(token)` to flip true via the USD trigger while very little of the curve supply has actually been sold, so `_prepareGraduationLiquidity` caches a very small `tokensForLP` alongside a comparatively large `ltFromPair`.
4. `_enterGraduating` fires, locking the token into `Lifecycle.Graduating` with these cached values.
5. Anyone calls `Bonding.finalizeGraduation(token)`. `_seedRebalancing` sees `pair.totalSupply() != 0`, computes `reserveToken`, `reserveLT` from the attacker's seeded reserves, and calls `_pairRebalance` → `_noFeeSwapInput(reserveIn, reserveOut, targetN, targetD, maxSwap)`.
6. `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` reverts because the quotient exceeds `type(uint256).max`.
7. Every subsequent call to `finalizeGraduation(token)` reverts identically (the cached `PendingGraduation` and attacker-set pair reserves never change), permanently freezing the curve-raised LT and the LP-bound tokens parked on `Bonding` for this token.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1498-1506)
```text
    ///      `Math.mulDiv` keeps the intermediate product
    ///      `reserveIn * reserveOut * targetN` inside its 512-bit working
    ///      space, but the final result `... / targetD` must still fit in
    ///      uint256. Call sites must keep that invariant — in practice
    ///      both the V2 uint112 reserve cap and the bound that
    ///      `tokensForLP` ≤ `LP_RESERVE` and `ltFromPair` ≤ raised LT
    ///      are well inside the safe envelope. Constructed adversarial
    ///      inputs that violate this would `revert` rather than silently
    ///      truncate, which is the correct failure mode.
```

**File:** packages/contracts/src/Bonding.sol (L1507-1522)
```text
    function _noFeeSwapInput(
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 targetN,
        uint256 targetD,
        uint256 maxSwap
    ) internal pure returns (uint256) {
        if (reserveIn == 0 || reserveOut == 0 || targetN == 0 || targetD == 0 || maxSwap == 0) {
            return 0;
        }
        uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
        uint256 newIn = Math.sqrt(product);
        if (newIn <= reserveIn) return 0;
        uint256 s = newIn - reserveIn;
        return s > maxSwap ? maxSwap : s;
    }
```
