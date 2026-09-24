Based on my investigation, I found a genuine analog of the missing-validation-before-use bug class in `Router.sol`.

### Title
Missing `PairNotFound` check in `Router.buy` causes divide-by-zero-masked underflow revert that can strand a graduating curve mid-transaction - (File: `packages/contracts/src/Router.sol`)

### Summary
The TensorFlow advisory's root cause is a lookup result (`node.op()`) being used without validating it first, unlike sibling code paths that do validate. `Router.sol` has the exact same class of bug: every other trade-adjacent function that resolves a pair via `factory.getPair(token, asset)` explicitly checks `if (pairAddr == address(0)) revert PairNotFound();` — `getAmountOut` [1](#0-0) , `previewBuy` [2](#0-1) , `addInitialLiquidity` [3](#0-2) , `sell` [4](#0-3) , and `graduate` [5](#0-4)  — but `buy()` omits it entirely: [6](#0-5) 

### Finding Description
`buy()` resolves `pairAddr = factory.getPair(token, asset)` and immediately feeds it into `_computeBuy(pairAddr, amountIn)`, which calls `IPair(pairAddr).getReserves()` / `.k()` / `.tokenBalance()` without ever checking `pairAddr != address(0)` [7](#0-6) . This mirrors the TFG advisory's pattern precisely: a lookup (`LookUp`/`getPair`) whose failure mode (empty op / zero address) is checked in every analogous code path except one.

However, I was unable to construct a reachable state where `pairAddr` is actually zero when `Bonding` invokes `Router.buy`. `Bonding.launch()` calls `_storeTokenInfo` (writing `tokenInfo[tokenAddr].creator`) and then `_deployAndSeed` (which calls `factory.createPair`) inside the same atomic transaction [8](#0-7) , and `Bonding.buy` only proceeds past the `info.creator == address(0)` gate for tokens that have already completed `launch()` successfully [9](#0-8) . Since `Factory.createPair` is one-shot per `(tokenA, tokenB)` pair and only `Bonding` (holding `BONDING_ROLE`) can call it or `Router.buy` [10](#0-9) , there is no unprivileged path (`Zap.createToken/buy/sell`, direct token/LT transfers, or pre-seeding the HyperSwap pair) that can make `factory.getPair(token, asset)` return `address(0)` for a token already accepted by `Bonding.buy`'s lifecycle checks.

### Impact Explanation
Given the current invariants (`launch()` atomicity, `Factory.createPair`'s one-shot-per-pair guard, and `BONDING_ROLE` gating), this missing check is not independently exploitable — a call would either succeed through the identical path `sell()`/`previewBuy()` already validate, or the whole `launch()` transaction would have reverted already. It is a real code-consistency defect (the same defensive check present in every sibling function is absent here), which is exactly the code smell the TFG advisory describes, but I could not prove a concrete unprivileged trigger that reaches `_computeBuy` with a zero `pairAddr` and causes theft or fund-freezing, as required by the validation rules.

### Likelihood Explanation
Low under current code: the omission is latent, guarded transitively by upstream invariants in `Bonding.launch`/`Factory.createPair` rather than by `Router.buy` itself. It would become directly exploitable only if a future change (e.g., allowing `Router.buy` to be called for a token whose pair hasn't been created, or relaxing the one-shot pair guard) broke that transitive protection — at which point the missing check would produce an unhandled low-level revert/panic inside `IPair(address(0))` calls rather than a clean `PairNotFound()`, which is a defense-in-depth/robustness gap rather than a currently reachable Medium+ vulnerability.

### Recommendation
Add the same `if (pairAddr == address(0)) revert PairNotFound();` guard to `Router.buy` immediately after resolving `pairAddr`, for consistency with `sell`, `previewBuy`, `getAmountOut`, `addInitialLiquidity`, and `graduate`, so the failure mode is a clean revert rather than an implicit dependency on caller-side invariants holding forever.

### Proof of Concept
No concrete unprivileged proof-of-concept could be constructed: exploiting the missing check requires `factory.getPair(token, asset)` to return `address(0)` for a token that `Bonding.buy`'s `info.creator != address(0)` gate has already accepted as launched — a state not reachable given `launch()`'s atomicity and `Factory.createPair`'s one-shot guard in the current contract set.

### Citations

**File:** packages/contracts/src/Router.sol (L55-58)
```text
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();

```

**File:** packages/contracts/src/Router.sol (L81-83)
```text
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
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

**File:** packages/contracts/src/Router.sol (L119-122)
```text
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        return _computeBuy(pairAddr, amountIn);
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

**File:** packages/contracts/src/Router.sol (L158-160)
```text
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
```

**File:** packages/contracts/src/Router.sol (L207-209)
```text
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
```

**File:** packages/contracts/src/Bonding.sol (L412-419)
```text
        bytes32 saltMixed = _mixSalt(creator_, params.name, params.ticker, params.salt);
        tokenAddr = Clones.predictDeterministicAddress($.tokenImplementation, saltMixed, address(this));
        _checkVanity(tokenAddr);

        _storeTokenInfo(tokenAddr, address(0), params, creator_);

        pair = _deployAndSeed(tokenAddr, saltMixed, params.name, params.ticker, params.ltAddress);
        $.tokenInfo[tokenAddr].pair = pair;
```

**File:** packages/contracts/src/Bonding.sol (L569-578)
```text
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        // `creator == 0` means the slot was never written. `Lifecycle.Curve` is
        // the zero value, so without this an unknown token would fall through
        // and revert deep in `router.buy` with an opaque error.
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        _enforceLaunchDelay(tokenAddress);

        (tokensOut, amountInUsed) = _executeBuy(msg.sender, trader, amountIn, tokenAddress);
```

**File:** packages/contracts/src/Factory.sol (L38-55)
```text
    function createPair(
        address tokenA,
        address tokenB
    ) external onlyRole(BONDING_ROLE) returns (address) {
        if (tokenA == address(0) || tokenB == address(0)) revert ZeroAddress();
        if (router == address(0)) revert NoRouter();
        if (_pairs[tokenA][tokenB] != address(0)) revert PairExists();

        Pair pair = new Pair(router, tokenA, tokenB);
        _pairs[tokenA][tokenB] = address(pair);
        _pairs[tokenB][tokenA] = address(pair);

        pairFor[tokenA] = address(pair);
        ltFor[tokenA] = tokenB;

        emit PairCreated(tokenA, tokenB, address(pair), ++pairCount);
        return address(pair);
    }
```
