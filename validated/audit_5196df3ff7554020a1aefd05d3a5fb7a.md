### Title
Graduation unconditionally burns any Token balance sitting in the Pair, seizing tokens a holder never committed to the curve - (File: packages/contracts/src/Bonding.sol)

### Summary
`Bonding._prepareGraduationLiquidity` treats the Pair's live `Token.balanceOf(pair)` as "unsold curve inventory" and burns the entire amount at graduation. Because `Pair.tokenBalance()` is a raw `balanceOf` read rather than an internally tracked curve-owned reserve, any Token that a holder sends directly to the Pair address via a plain ERC20 `transfer` — without ever routing through `Zap.sell`/`Bonding.sell` — is burned along with the genuine unsold supply the moment the token graduates. The holder never "entered the market" (never traded through the curve) yet the protocol seizes and permanently destroys their tokens.

### Finding Description
`_prepareGraduationLiquidity` computes the amount to burn as a live balance read, not as `curveSupply - sold`: [1](#0-0) 

`Pair.tokenBalance()` simply returns `IERC20(launchedToken).balanceOf(address(this))`: [2](#0-1) 

`Token.burn` is owner-gated (owner = `Bonding`) and burns from an arbitrary address with no approval required: [3](#0-2) 

Because `tokenBalance()` is a live balance rather than a tracked "sold from curve" counter, it cannot distinguish tokens that are legitimately unsold curve inventory from tokens an unrelated holder chose to send directly into the Pair (e.g., by mistake, or to try to seed liquidity manually, or simply by copying the Pair address instead of calling `Zap.sell`). The project's own documentation confirms this is exactly what happens: "Burn any unsold real curve tokens from the pair (`unsoldBurned`). This also burns any tokens donated to the pair via direct ERC20 transfer," and it is explicitly one of the tested invariants (`#7 Donation resistance`). [4](#0-3) 

This is precisely the bug class described in the external report: an asset (here, the launched Token) is seized/destroyed by protocol logic (`_enterGraduating` → `_prepareGraduationLiquidity`) even though the owner never opted into the mechanism that consumes it (curve trading via `Zap`/`Bonding`). There is no analog of `enterMarket` gating which balances the protocol is allowed to treat as its own — any Token balance physically present in the Pair when graduation fires is claimed.

Note the asymmetry with the LT side of the same function: donated LT sitting in the pair is *excluded* from `ltFromPair` and left untouched (merely locked, not destroyed) — [5](#0-4) 

— while the Token side has no equivalent protection and is unconditionally burned, which is strictly worse than "locked" since burning is irreversible under any circumstance, including a future protocol upgrade.

### Impact Explanation
Any Token balance directly transferred into the Pair contract by a holder — via a plain `IERC20.transfer(pairAddress, amount)` call, which requires no special permission and is reachable by any unrelated wallet — is permanently destroyed the moment the token graduates (whichever trigger fires first: USD threshold or full curve sellout). This is an unrecoverable, total loss of the transferred tokens for the sender, who at no point authorized the protocol to consume that specific balance through the curve. This satisfies "permanent freezing/destruction of trader funds."

### Likelihood Explanation
Graduation is a normal, expected, permissionless event for every launched token — `finalizeGraduation` runs on essentially every successful token (via the USD or supply trigger), so the burn logic executes routinely, not as an edge case. The only precondition is that some Token balance is sitting in the Pair from a direct transfer at the time graduation's phase 1 (`_enterGraduating`/`_prepareGraduationLiquidity`) fires — reachable by any unrelated wallet sending tokens straight to the Pair address instead of using `Zap.sell`, which is an explicitly in-scope, unprivileged action.

### Recommendation
Track curve-owned token supply internally (e.g., `curveSupply - cumulativeSold`) rather than reading the Pair's live `balanceOf`, and burn only that tracked amount. Any balance beyond the tracked curve-owned amount (i.e., tokens that arrived via a bare ERC20 transfer rather than through `Router.buy`/`Router.sell`) should be excluded from `unsoldBurned` and either left untouched/locked (mirroring how donated LT is already excluded from `ltFromPair`) or routed through an explicit, non-destructive rescue path, so that a holder's tokens are never seized by graduation logic they never opted into by trading through the curve.

### Proof of Concept
1. `Bonding.launch` creates `tokenAddress`/`pairAddr` normally; the curve trades as usual via `Zap.buy`/`Zap.sell`.
2. At any point before graduation, an unrelated wallet holding `Token` calls `Token.transfer(pairAddr, X)` directly (no approval to Pair/Router required, no interaction with `Zap`/`Bonding` needed).
3. The token subsequently graduates (USD or supply trigger) and a buy triggers `_enterGraduating` → `_prepareGraduationLiquidity`:
   - `unsoldBurned = IPair(pairAddr).tokenBalance()` now includes the donor's `X` tokens on top of genuine unsold curve inventory.
   - `Token(tokenAddress).burn(pairAddr, unsoldBurned)` destroys all of it, including the donor's `X` tokens.
4. The donor's `X` tokens are gone forever; they never called `Zap.sell`/`Bonding.sell` and never consented to the curve consuming that balance. `docs/contracts-scope.md`'s own description ("This also burns any tokens donated to the pair via direct ERC20 transfer") and invariant `#7` in `test/GraduationInvariants.t.sol` confirm this is the exact, reproducible behavior of `_prepareGraduationLiquidity`.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1073-1082)
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
```

**File:** packages/contracts/src/Bonding.sol (L1084-1087)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }
```

**File:** packages/contracts/src/Pair.sol (L103-105)
```text
    function tokenBalance() external view returns (uint256) {
        return IERC20(launchedToken).balanceOf(address(this));
    }
```

**File:** packages/contracts/src/Token.sol (L37-43)
```text
    /// @notice Burn from any address. Owner only, no approval required.
    function burn(
        address from,
        uint256 amount
    ) external onlyOwner {
        _burn(from, amount);
    }
```

**File:** docs/contracts-scope.md (L87-89)
```markdown
1. Read `(reserve0, reserve1)` from the Pair **before** any state mutation.
2. Burn any unsold real curve tokens from the pair (`unsoldBurned`). This also burns any tokens donated to the pair via direct ERC20 transfer.
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
```
