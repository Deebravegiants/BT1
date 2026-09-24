### Title
`Router.buy` skips the `pairAddr == address(0)` validation present in `sell`/`previewBuy`, letting a call against an unpaired token burn the trader's LT into a zero-value swap - ([File: packages/contracts/src/Router.sol])

### Summary
`Router.sell` and `Router.previewBuy` both validate `pairAddr != address(0)` before touching `IPair(pairAddr)`, but `Router.buy` omits this check entirely. This is the same bug class as CVE-2023-38430: a request handler that trusts an unvalidated discriminator (there, the SMB protocol ID; here, the existence of a real `Pair` contract behind `pairAddr`) and proceeds straight into reads/calls against that unvalidated value.

### Finding Description [1](#0-0) 

```solidity
function buy(
    uint256 amountIn,
    address token,
    address to
) external onlyRole(BONDING_ROLE) returns (uint256 amountInUsed, uint256 tokensOut) {
    if (amountIn == 0) revert ZeroAmount();

    address asset = assetTokenFor(token);
    address pairAddr = factory.getPair(token, asset);
    // <-- MISSING: no `if (pairAddr == address(0)) revert PairNotFound();`

    (amountInUsed, tokensOut) = _computeBuy(pairAddr, amountIn);

    IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed);

    IPair(pairAddr).transferToken(to, tokensOut);
    IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0);
}
```

Compare against `sell` and `previewBuy`, which both perform the guard: [2](#0-1) [3](#0-2) 

If `pairAddr` resolves to `address(0)` (or any address with no `Pair` bytecode), `_computeBuy(pairAddr, amountIn)` calls `IPair(pairAddr).getReserves()` / `.k()` / `.tokenBalance()` against a non-contract address. Under Solidity's low-level-call semantics for external calls to an address with no code, these calls return empty data that decodes as all-zero return values rather than reverting, so `_computeBuy` proceeds with `reserveToken = 0`, `reserveAsset = 0`, `k = 0`, producing `tokensOut = 0` and `amountInUsed = amountIn` (uncapped, since the capping branch is never entered when the real balance is also read as `0`). `buy()` then executes `IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed)` — sending the trader's real LT to `pairAddr` (potentially `address(0)`, i.e. burning it) — followed by calls to `transferToken`/`swap` on the same non-existent pair.

### Impact Explanation
The direct consequence of reaching this path is a real, non-refundable loss of the trader's LT (sent to `address(0)` or an uncontrolled address) for zero tokens received — the same "unvalidated discriminator → downstream read against unexpected/garbage state" root cause as the ksmbd CVE, mapped onto alt.fun's bonding-curve AMM layer. This satisfies the "concrete theft or permanent freezing of trader funds" bar. Note: `Router.buy` is restricted to `BONDING_ROLE`, held only by `Bonding`, and `Bonding.buy` itself gates on `TokenInfo.creator != address(0)` before calling into `Router`. Whether an unprivileged trader can force `factory.getPair(token, asset)` to resolve to `address(0)` for a token that already passed `Bonding`'s `creator != 0` gate depends on Factory's multi-LT `ltFor`/`getPair` bookkeeping (whether `assetTokenFor(token)` can ever diverge from the LT actually paired at launch, e.g. via a stale/second `PairCreated(lt)` registration for the same token). I could not fully verify Factory.sol's `createPair`/`ltFor`/`getPair` implementation within the available tool budget, so the exact reachability from an unprivileged transaction is unconfirmed — this is the key open question a follow-up review must close before treating this as a confirmed, exploitable Critical.

### Likelihood Explanation
Likelihood is Medium given the current uncertainty: the missing check is a genuine code-inconsistency defect (present in `sell`/`previewBuy`, absent in `buy`), but whether it is reachable by an ordinary trader hinges on Factory's pair-registry invariants (single `getPair(token, ltFor(token))` mapping per token) holding at all times, including any future multi-LT or Factory-owner-driven repointing. If those invariants can ever be broken or raced by a permissionless caller, likelihood rises to High.

### Recommendation
Add the same guard `Router.sell`/`Router.previewBuy` already have to `Router.buy`:
```solidity
address pairAddr = factory.getPair(token, asset);
if (pairAddr == address(0)) revert PairNotFound();
```
placed immediately before the `_computeBuy` call, so a null/garbage pair address reverts instead of silently proceeding into a zero-value swap.

### Proof of Concept
Conceptual PoC (exact preconditions to instantiate depend on the Factory invariant noted above, which I was unable to confirm within the available budget):
1. Arrange for `factory.getPair(token, factory.ltFor(token))` to resolve to `address(0)` for a `token` that still passes `Bonding.buy`'s `TokenInfo.creator != address(0)` / `Lifecycle.Curve` gate (e.g. exploiting any Factory registry edge case that decouples `tokenInfo[token].pair` from what `Factory.getPair`/`ltFor` currently report).
2. Call `Bonding.buy(amountIn, token, 0, trader)` through an allowlisted `Zap` (e.g. `Zap.buy`).
3. `Router.buy` proceeds without the `PairNotFound` check, `_computeBuy` returns `tokensOut = 0` against zeroed reserves, and `amountInUsed = amountIn` LT is transferred via `safeTransferFrom(to, pairAddr, amountInUsed)` to the unvalidated `pairAddr` — the trader's LT is lost for zero tokens.

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
