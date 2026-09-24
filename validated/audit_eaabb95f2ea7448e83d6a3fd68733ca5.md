Based on my research, I found a genuine incomplete-comparison bug: `Router.buy` is missing the `pairAddr == address(0)` guard that every sibling entry point (`sell`, `previewBuy`, `getAmountOut`) enforces.

### Title
`Router.buy` omits the `PairNotFound` zero-address check present in every sibling entry point, letting a degenerate pair address silently reach `_computeBuy`/`Pair.swap` - (File: packages/contracts/src/Router.sol)

### Summary
`Router.sell`, `Router.previewBuy`, and `Router.getAmountOut` all validate `pairAddr != address(0)` immediately after `factory.getPair(...)` before touching the pair. `Router.buy` — the function `Bonding.buy` calls on every single curve trade — omits this same comparison factor.

### Finding Description
Compare the four Router entry points that resolve a pair via `factory.getPair(token, asset)`: [1](#0-0) 

```solidity
function buy(...) external onlyRole(BONDING_ROLE) returns (uint256 amountInUsed, uint256 tokensOut) {
    if (amountIn == 0) revert ZeroAmount();
    address asset = assetTokenFor(token);
    address pairAddr = factory.getPair(token, asset);
    (amountInUsed, tokensOut) = _computeBuy(pairAddr, amountIn);   // <-- no PairNotFound check
    ...
}
```

versus `sell`, which performs the identical resolution but adds the missing comparison: [2](#0-1) 

and `previewBuy`: [3](#0-2) 

`buy` is the odd one out — the exact GitLab-report bug class ("incomplete comparison, missing factors": one code path checks a condition that a structurally-identical sibling path omits), just in Solidity form instead of hostname validation.

### Impact Explanation
In the current wiring this is unreachable in practice: `Factory.createPair` is called exactly once per launched token from `Bonding.launch` before any `buy` can occur, so `factory.getPair(token, asset)` is always populated by the time `Bonding.buy` → `Router.buy` executes for a real token, and `Bonding.creatorOf` / `isTrading` gates in `Zap`/`Bonding` already reject unknown tokens earlier in the call chain. I could not identify a caller-reachable path where `Bonding.buy(amountIn, token, minOut, trader)` is invoked for a `token` that has no registered pair while still passing `Bonding`'s own `Lifecycle.Curve` gate — the `TokenInfo.pair` field and `Factory.pairFor` are set atomically at `launch` and never cleared. Because of that, this is best characterized as a latent defensive-check gap (would surface as an unhandled low-level revert instead of the clean `PairNotFound` error) rather than a currently exploitable fund-loss or freezing bug reachable by an unprivileged trader, creator, or LP. It does not meet the "concrete theft or permanent freezing of funds" bar required by the Validate section.

### Likelihood Explanation
Low under the current `Bonding`/`Factory`/`Zap` wiring, since every caller path that can reach `Router.buy` already implies a registered pair. The gap would only become live if a future change (e.g., a multi-LT re-pointing path, or a `Bonding` upgrade that lets `buy` be called against a token whose pair was somehow never created or was cleared) removed that upstream guarantee — at which point the missing check would degrade a clean revert into an unhandled internal failure inside `_computeBuy`/`Pair.getReserves()`.

### Recommendation
Add the same guard the sibling functions already have, for defense-in-depth and consistency, even though it is not currently reachable:
```solidity
address pairAddr = factory.getPair(token, asset);
if (pairAddr == address(0)) revert PairNotFound();
```

### Proof of Concept
Not applicable as a live exploit — I was unable to construct an unprivileged-caller sequence that reaches `Router.buy` with an unregistered pair given `Bonding.launch`'s atomic pair creation and the `Lifecycle.Curve` gates in `Bonding`/`Zap`. This finding is reported as a code-consistency/defense-in-depth gap rather than a demonstrated fund-loss exploit, per the task's requirement to only accept concrete theft/freezing impacts — flagging it transparently since it is the closest analog to the GitLab "incomplete comparison with missing factors" bug class found in the in-scope contracts.

### Citations

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

**File:** packages/contracts/src/Router.sol (L151-163)
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
```
