### Title
`Router.buy` skips the zero-pair guard that every other AMM entry point enforces - ([File: packages/contracts/src/Router.sol])

### Summary
`Router.sol` derives `pairAddr = factory.getPair(token, asset)` in four places — `getAmountOut`, `buy`, `previewBuy`, and `sell` — and three of them explicitly guard against `pairAddr == address(0)` with `revert PairNotFound()` before touching `IPair(pairAddr)`. `buy` is the exception: it computes `pairAddr` and immediately feeds it into `_computeBuy(pairAddr, amountIn)`, which calls `pair.getReserves()`, `pair.k()`, and `pair.tokenBalance()` on that address with no existence check at all. [1](#0-0) 

### Finding Description
Compare the four call sites:

- `getAmountOut` — guards with `if (pairAddr == address(0)) revert PairNotFound();` before calling `_computeBuy`/reading reserves. [2](#0-1) 
- `previewBuy` — same explicit guard before calling `_computeBuy`. [3](#0-2) 
- `sell` — same explicit guard before calling `_computeSell`/`transferAsset`/`swap`. [4](#0-3) 
- `buy` — **no guard**. It resolves `pairAddr` and passes it straight into `_computeBuy`, then into `IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed)`, `IPair(pairAddr).transferToken`, and `IPair(pairAddr).swap`. [1](#0-0) 

This is structurally the same defect class as the CVE: a validation guard (`PairNotFound`/"MAC header valid") that the codebase clearly intends to apply to every path touching pair state was written into three of the four sibling functions but omitted from one, leaving that one path free to dereference an unvalidated/absent target (`eth_hdr(skb)` in the kernel case, `IPair(pairAddr)` here) before any check occurs.

### Impact Explanation
In the current call graph, `Router.buy` is only reachable via `BONDING_ROLE`, held solely by `Bonding`, and `Bonding` only calls it for tokens it has itself `launch`ed (which always creates a `Pair` synchronously in `Bonding.launch`/`_deployAndSeed`), so `pairAddr` should never actually be zero in the intended flow. Because of this, I cannot demonstrate a concrete, currently-reachable path from an unprivileged trader to a zero `pairAddr` in `buy()` — the missing check is a real inconsistency in the code (violating the codebase's own established invariant that every `IPair(pairAddr)` dereference in `Router.sol` must be preceded by a `PairNotFound` guard), but under today's `Bonding`/`Factory` wiring it does not appear to be independently triggerable by a trader, creator, or unrelated wallet with a distinct pre-condition that bypasses `Bonding.launch`'s pair creation. Even if it were reached with `pairAddr == address(0)`, the failure mode is a revert (Solidity's external-call return-data decoding fails against code-less `address(0)`), not a state-corrupting write, silent success, or fund movement — so it would manifest as a DoS/revert rather than theft or fund freezing.

### Likelihood Explanation
Low under the current, single-instance `Bonding`/`Factory`/`Router` wiring, since `Router.buy`'s `BONDING_ROLE` is restricted to `Bonding`, and `Bonding` always creates the `Pair` before any `buy()` call can reference it. The missing guard is a genuine deviation from the pattern enforced everywhere else in the same file, and would become a live risk if `Router` were ever pointed at a `Factory` state where a token/LT pairing could be queried before pair creation (e.g., a future multi-router/registration ordering change, or a `Factory` bug that lets `getPair` be queried for a token that failed mid-launch) — but I could not find a currently-reachable unprivileged transaction sequence that hits this exact line with a zero pair address.

### Recommendation
Add the same `if (pairAddr == address(0)) revert PairNotFound();` check to `Router.buy` immediately after resolving `pairAddr`, mirroring `previewBuy`/`sell`/`getAmountOut`, so all four sibling entry points enforce the invariant uniformly regardless of future changes to `Bonding`/`Factory` sequencing.

### Proof of Concept
Not reproducible against the current deployed wiring: `Bonding.launch` always creates the `Pair` in the same transaction before any external actor can call `Zap.buy → Bonding.buy → Router.buy` for that token, so `factory.getPair(token, asset)` cannot return `address(0)` at the point `Router.buy` is invoked today. A concrete PoC would require either (a) a future code change that lets `Router.buy` be called for a token/LT pairing before `Factory.createPair` runs, or (b) a `Factory`/`Bonding` bug that registers a token in `Bonding`'s `tokenInfo` before its `Pair` exists — neither of which exists in the code as currently written. This finding is reported as a code-consistency/defense-in-depth gap analogous to the CVE's pattern (a guard applied inconsistently across sibling code paths that touch the same unvalidated resource), not as a demonstrated exploit under the present contract wiring.

### Citations

**File:** packages/contracts/src/Router.sol (L50-69)
```text
    function getAmountOut(
        address token,
        bool isBuy,
        uint256 amountIn
    ) public view returns (uint256) {
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();

        if (isBuy) {
            (, uint256 tokensOut) = _computeBuy(pairAddr, amountIn);
            return tokensOut;
        }

        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 newReserveToken = reserveToken + amountIn;
        uint256 newReserveAsset = pair.k() / newReserveToken;
        return reserveAsset - newReserveAsset;
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

**File:** packages/contracts/src/Router.sol (L114-123)
```text
    function previewBuy(
        address token,
        uint256 amountIn
    ) external view returns (uint256 amountInUsed, uint256 tokensOut) {
        if (amountIn == 0) revert ZeroAmount();
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        return _computeBuy(pairAddr, amountIn);
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
