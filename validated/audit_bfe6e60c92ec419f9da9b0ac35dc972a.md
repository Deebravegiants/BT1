### Title
`Router.buy`/`Router.sell` credit `Pair`'s stored reserves with the nominal transferred amount instead of the balance actually received, letting any shortfall on the LT or launched-token transfer create unbacked reserve inflation - (File: `packages/contracts/src/Router.sol`)

### Summary
`Router.buy` and `Router.sell` move the reserve asset (LT) and the launched `Token` into the `Pair` via `safeTransferFrom`, then unconditionally call `Pair.swap(...)` with the *nominal* amount requested, not the amount the pair actually received. `Pair.swap` blindly adds that nominal amount to its internal `_pool.assetReserve` / `_pool.tokenReserve` counters. If the transfer delivers less than the nominal amount — the exact deflationary/rebasing-token risk class described in the report — the stored reserve becomes permanently inflated relative to the pair's real token balance, which is later relied upon by graduation (`Router.graduate`) to drain "real LT raised" out of the pair.

### Finding Description
`Router.buy`:
```solidity
IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed);
IPair(pairAddr).transferToken(to, tokensOut);
IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0);
``` [1](#0-0) 

`Router.sell` follows the identical pattern for the launched `Token`:
```solidity
IERC20(token).safeTransferFrom(to, pairAddr, amountIn);
assetOut = _computeSell(pairAddr, amountIn);
IPair(pairAddr).transferAsset(to, assetOut);
IPair(pairAddr).swap(amountIn, 0, 0, assetOut);
``` [2](#0-1) 

`Pair.swap` never checks the pair's actual token balance against the claimed `assetIn`/`tokenIn`; it simply adds the passed-in values to the stored reserves and checks the K-invariant against those *stored* numbers, not against `IERC20.balanceOf(address(this))`:
```solidity
function swap(uint256 tokenIn, uint256 tokenOut, uint256 assetIn, uint256 assetOut) external onlyRouter returns (bool) {
    uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
    uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
    if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();
    _pool.tokenReserve = newTokenReserve;
    _pool.assetReserve = newAssetReserve;
    ...
}
``` [3](#0-2) 

This is precisely the bug class in the external report: the code assumes `safeTransferFrom`'s nominal amount equals what the recipient actually received, and never reconciles against the real balance. On alt.fun's real shape, this reserve is the "real LT raised", which graduation later drains via `Router.graduate`:
```solidity
function graduate(address token, uint256 amount) external onlyRole(BONDING_ROLE) {
    ...
    IPair(pairAddr).transferAsset(msg.sender, amount);
}
``` [4](#0-3) 
where `amount = storedAssetReserve - virtualLtReserve` is computed purely from the pair's *stored* `_pool.assetReserve`, per the documented graduation flow: `ltFromPair = reserve1 - virtualLtReserve`, drained via `Router.graduate(token, ltFromPair)` [5](#0-4) . If the stored `assetReserve` is inflated above the pair's real LT balance (because a prior `Router.buy` credited a nominal `amountInUsed` that wasn't fully received), `Router.graduate`'s `Pair.transferAsset` will either revert (bricking finalization) or, if slack exists from other buyers' genuinely-received LT, drain more real LT out of the pair than this trader actually contributed — socializing the shortfall onto other traders/LPs and skewing the HyperSwap LP seed price away from the true curve-close price (`tokensForLP = ltFromPair × reserve0 / reserve1` is then computed from a phantom `reserve1`).

The `_computeBuy`/`_computeSell` cap logic in `Router.sol` only checks the pair's real `tokenBalance()` against the *launched token* side [6](#0-5)  — there is no equivalent balance reconciliation on the *asset* (LT) side of either `buy` or `sell`.

### Impact Explanation
Any shortfall between the nominal `amountInUsed`/`amountIn` passed to `safeTransferFrom` and the actual amount credited to the `Pair` is silently absorbed into `_pool.assetReserve`/`tokenReserve` as phantom liquidity. Since graduation's `ltFromPair` and `tokensForLP` computations, and every subsequent `getReserves()`-based quote (`_computeBuy`/`_computeSell`), trust these stored reserves rather than live balances, an inflated reserve leads to: (1) `Router.graduate`'s `transferAsset` reverting and permanently bricking `finalizeGraduation` for that token (freezing curve-raised LT and the 250M reserved tokens on `Bonding`), or (2) draining more real LT than the curve actually holds, at the expense of other traders/LPs, and seeding the HyperSwap LP at a price divorced from the real curve-close price — both are Medium/High-severity insolvency/fund-freezing outcomes reachable purely through `Zap.buy`/`Zap.sell` → `Bonding.buy`/`sell` → `Router.buy`/`sell`, i.e. from an ordinary trader transaction.

### Likelihood Explanation
Likelihood depends entirely on whether the reserve asset (the BounceTech LT) or the launched `Token` can ever deliver less than the nominal transferred amount on `transferFrom` — e.g., a future fee-on-transfer/rebase behavior in the LT, or any ERC20 edge case in the launched `Token`/LT pairing that alt.fun does not control (the LT is an external, upgradeable, third-party contract; `AGENTS.md`/docs explicitly flag that BounceTech can redeploy/retire LTs). Given the LT is external and out of alt.fun's control, and the protocol explicitly builds around HyperSwap's fee-on-transfer-only swap selectors [7](#0-6) , the assumption that transferred amounts always land in full is not structurally enforced in `Router.sol`/`Pair.sol`, making this a real, if conditional, root-cause weakness rather than a purely theoretical one.

### Recommendation
In `Router.buy` and `Router.sell`, snapshot the `Pair`'s real balance of the asset/token being transferred in immediately before and after the `safeTransferFrom`, and pass the *actual delta* (not the nominal `amountInUsed`/`amountIn`) into `Pair.swap`. Alternatively, have `Pair.swap` itself reconcile `IERC20.balanceOf(address(this))` against the claimed `tokenIn`/`assetIn` and revert (or clamp) on any shortfall, mirroring the existing `tokenBalance()`-based overflow cap already used in `_computeBuy`. Short-term, explicitly document/enforce that only LTs verified to have standard (non-fee, non-rebasing) `transfer`/`transferFrom` semantics can be paired via `Bonding.launch`.

### Proof of Concept
1. A malicious or future BounceTech LT deployment (or any LT that later adds a transfer fee — the LT is external and upgradeable per the "Retired LTs" note in `docs/contracts-scope.md`) is paired with a token at launch via `Bonding.launch`.
2. A trader calls `Zap.buy(tokenAddress, usdcAmount, 0, referrer)`. `Zap` mints LT via `IBounceLeveragedToken(lt).mint(...)` and calls `Bonding.buy` → `Router.buy(amountIn, token, to)`.
3. `Router.buy` calls `IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed)`. If the LT's `transferFrom` implementation ever takes a fee (deflationary transfer), the `Pair` receives `amountInUsed - fee` real LT.
4. `Router.buy` still calls `IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0)`, crediting the pair's stored `assetReserve` with the full nominal `amountInUsed`, not `amountInUsed - fee`.
5. Repeat across buys until graduation triggers. `Bonding._prepareGraduationLiquidity`/`Router.graduate` computes `ltFromPair = storedAssetReserve - virtualLtReserve` and attempts to transfer that amount out of the pair via `Pair.transferAsset` → `IERC20(assetToken).safeTransfer`. Because the pair's real LT balance is now less than the stored `assetReserve` implies, this either reverts (bricking `finalizeGraduation` permanently for that token) or drains real LT contributed by other traders to cover the shortfall, corrupting the LP-seed price invariant.

### Citations

**File:** packages/contracts/src/Router.sol (L104-107)
```text
        IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed);

        IPair(pairAddr).transferToken(to, tokensOut);
        IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0);
```

**File:** packages/contracts/src/Router.sol (L140-147)
```text
        uint256 realBalance = pair.tokenBalance();
        if (tokensOut > realBalance) {
            tokensOut = realBalance;
            uint256 cappedReserveToken = reserveToken - tokensOut;
            if (cappedReserveToken == 0) revert OverflowCapDegenerate();
            uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
            amountInUsed = cappedReserveAsset - reserveAsset;
        }
```

**File:** packages/contracts/src/Router.sol (L163-169)
```text
        IERC20(token).safeTransferFrom(to, pairAddr, amountIn);

        assetOut = _computeSell(pairAddr, amountIn);

        IPair(pairAddr).transferAsset(to, assetOut);

        IPair(pairAddr).swap(amountIn, 0, 0, assetOut);
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

**File:** docs/contracts-scope.md (L89-90)
```markdown
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
4. Compute `tokensForLP = (ltFromPair × reserve0) / reserve1` — the unique amount that sets the LP price `ltFromPair / tokensForLP` equal to the last curve price `reserve1 / reserve0`. Capped at `lpReserveTotal` as a defensive guard (parabola math proves `tokensForLP ≤ lpReserveTotal` by construction).
```

**File:** packages/contracts/AGENTS.md (L95-107)
```markdown
## HyperSwap Router non-standard ABI (Read This Before Adding Any Router Call)

HyperSwap's mainnet V2 router (`0xb4a9C4e6Ea8E2191d2FA5B380452a634Fb21240A`) is **not** a vanilla `UniswapV2Router02`. The selector dispatch table omits every canonical swap function and replaces them with three FoT-only variants that take a non-standard `address referrer` argument inserted between `to` and `deadline`:

| Selector | Function (HyperSwap) | Canonical V2 equivalent (NOT exposed) |
|---|---|---|
| `0xac3893ba` | `swapExactTokensForTokensSupportingFeeOnTransferTokens(uint,uint,address[],address,address,uint)` | `swapExactTokensForTokens(...)` (`0x38ed1739`) |
| `0xb4822be3` | `swapExactETHForTokensSupportingFeeOnTransferTokens(uint,address[],address,address,uint)` | `swapExactETHForTokens(...)` (`0x7ff36ab5`) |
| `0x52aa4c22` | `swapExactTokensForETHSupportingFeeOnTransferTokens(uint,uint,address[],address,address,uint)` | `swapExactTokensForETH(...)` (`0x18cbafe5`) |

**Calling the canonical selector reverts with no data** (selector not in the dispatch table → fallback). A router swap call in the hostile-pre-seed defense would brick affected graduations on mainnet.

**The protocol's rule: never call a swap function on the V2 router.** Both `Bonding._pairRebalance` (the hostile-pre-seed rebalance) and `Zap._swapOnUniswapV2` (post-grad user trades) go direct to the pair via `pair.swap(amount0Out, amount1Out, to, "")`. We read the output from the pair's own fee-aware `getAmountOut` quote; the pair's K-invariant check enforces correctness. This is independent of HyperSwap's router quirks and works on any V2 fork.
```
