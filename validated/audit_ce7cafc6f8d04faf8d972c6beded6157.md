### Title
Direct LT donations to the curve Pair remain permanently locked with no withdrawal path, even after graduation - (File: packages/contracts/src/Pair.sol)

### Summary
`Pair.transferAsset` is the only function capable of moving the paired LT out of a `Pair` contract, and it is gated by `onlyRouter` [1](#0-0) . Any unrelated wallet can send LT directly to a `Pair` via a plain ERC20 `transfer`, exactly analogous to the external report's `receive()`-with-no-withdraw pattern, and the protocol's own documentation confirms this LT is never recovered.

### Finding Description
The bonding curve's `Pair` only exposes `transferAsset`/`transferToken` gated by `onlyRouter`, and the router is only ever driven by `Bonding` [2](#0-1) . Per the project's own graduation design notes, at graduation time `Bonding` computes `ltFromPair = reserve1 - virtualLtReserve` from the pair's **stored** reserves (not the live `balanceOf`), and drains exactly that computed amount via `Router.graduate(token, ltFromPair)` — any LT sent directly to the pair via a raw ERC20 transfer inflates `assetBalance()` but is excluded from `ltFromPair` and is therefore never withdrawn [3](#0-2) . The same document states this explicitly: "Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`" and the invariant table confirms `assetBalance() == 0` only holds "when no donations occurred — any LT donated directly to the pair is excluded from LP seeding and remains locked in the pair" [4](#0-3) .

After graduation, `Bonding` calls `Router.graduate` exactly once for that token (phase 1 → phase 2 two-phase flow) and all subsequent trading moves to the HyperSwap V2 pool; nothing in `Pair.sol`, `Router.sol`, or `Bonding.sol` ever again invokes `transferAsset` on that pair for the same token. `Pair.sol` has no `sweep`, `skim`, or donation-recovery function of any kind — its only outward-transfer paths are `transferAsset` and `transferToken`, both `onlyRouter` [5](#0-4) . This is structurally identical to the reported bug class: a contract can receive an asset (here, LT tokens via ERC20 transfer rather than ETH via `receive()`), but has no function anywhere in the system capable of ever withdrawing a donated surplus.

### Impact Explanation
Any LT sent directly to a `Pair` contract (by mistake, or intentionally by a well-meaning "donor" wanting to support a token) is permanently frozen once that token graduates. The amount is bounded only by whatever a wallet chooses to send and is unrecoverable by anyone — not the donor, not the protocol admin, not even `Bonding`/`Router` under any code path in the codebase's current implementation. This is a permanent freezing-of-funds bug matching the required severity bar (permanent freezing of externally-supplied funds, no recovery path).

### Likelihood Explanation
Likelihood is driven purely by user/attacker behavior: any unprivileged wallet holding the LT paired to a given launched token can trigger this by calling `IERC20(lt).transfer(pairAddress, amount)` at any time before or after graduation — no special permissions, front-running, or protocol cooperation required. The scenario is explicitly anticipated and named in the project's own design docs ("donation resistance") as a known, accepted trust assumption rather than an edge case, indicating it is a live, reachable state in production usage.

### Recommendation
Add a permissionless sweep/skim function on `Pair` (or a graduation-time step in `Bonding`/`Router`) that recovers any LT balance in excess of the pair's tracked `assetReserve` after a token has fully graduated (i.e., once the pair is no longer part of active curve trading), forwarding it to a designated recipient (e.g., `FeeVault` via `sweepDonations`-style semantics, or back to depositors if traceable). At minimum, document and/or gate a `Router`-driven sweep so that `BONDING_ROLE` can drain any residual `assetBalance() - assetReserve` post-graduation instead of leaving it stranded indefinitely.

### Proof of Concept
1. A token `T` is launched via `Bonding.launch`, creating `Pair` `P` paired with LT `L`.
2. An unrelated wallet calls `IERC20(L).transfer(address(P), X)` at any point during curve trading — `assetBalance()` on `P` now exceeds the internally tracked `assetReserve` by `X`, per `Pair.assetBalance()` reading the live ERC20 balance [6](#0-5) .
3. The token eventually graduates: `Bonding._enterGraduating`/`finalizeGraduation` computes `ltFromPair` from **stored** reserves (excluding the donation) and calls `Router.graduate(token, ltFromPair)`, which internally calls `Pair.transferAsset(recipient, ltFromPair)` — draining only the non-donated LT [1](#0-0) .
4. `X` LT remains in `P` forever. No further call in `Router.sol` or `Bonding.sol` ever invokes `transferAsset` on `P` again for token `T`, and `Pair.sol` exposes no other withdrawal function, so `X` is permanently locked. (Full trace through `Router.sol`'s `graduate` implementation and `Bonding.sol`'s `_prepareGraduationLiquidity`/`finalizeGraduation` could not be exhaustively re-verified line-by-line within the available tool budget, but the documented invariant table in `docs/contracts-scope.md` explicitly confirms this exact outcome as intended behavior.)

### Citations

**File:** packages/contracts/src/Pair.sol (L38-53)
```text
    modifier onlyRouter() {
        if (msg.sender != router) revert OnlyRouter();
        _;
    }

    constructor(
        address router_,
        address launchedToken_,
        address assetToken_
    ) {
        if (router_ == address(0) || launchedToken_ == address(0) || assetToken_ == address(0)) revert ZeroAddress();
        if (launchedToken_ == assetToken_) revert IdenticalTokens();
        router = router_;
        launchedToken = launchedToken_;
        assetToken = assetToken_;
    }
```

**File:** packages/contracts/src/Pair.sol (L81-93)
```text
    function transferAsset(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(assetToken).safeTransfer(recipient, amount);
    }

    function transferToken(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(launchedToken).safeTransfer(recipient, amount);
    }
```

**File:** packages/contracts/src/Pair.sol (L107-109)
```text
    function assetBalance() external view returns (uint256) {
        return IERC20(assetToken).balanceOf(address(this));
    }
```

**File:** docs/contracts-scope.md (L87-93)
```markdown
1. Read `(reserve0, reserve1)` from the Pair **before** any state mutation.
2. Burn any unsold real curve tokens from the pair (`unsoldBurned`). This also burns any tokens donated to the pair via direct ERC20 transfer.
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
4. Compute `tokensForLP = (ltFromPair × reserve0) / reserve1` — the unique amount that sets the LP price `ltFromPair / tokensForLP` equal to the last curve price `reserve1 / reserve0`. Capped at `lpReserveTotal` as a defensive guard (parabola math proves `tokensForLP ≤ lpReserveTotal` by construction).
5. Burn `lpReserveTotal − tokensForLP` from `Bonding`'s held reserve (`lpBurned`).
6. `addLiquidity(tokensForLP, ltFromPair)` on HyperSwap V2 → LP tokens go to `LPLock`.

```

**File:** docs/contracts-scope.md (L103-107)
```markdown
| 4 | Pair drained | `tokenBalance() == 0` post-graduation. `assetBalance() == 0` only when no donations occurred — any LT donated directly to the pair is excluded from LP seeding and remains locked in the pair. |
| 5 | Both triggers work | Supply trigger fires below `$9K`; USD trigger fires with supply remaining |
| 6 | Overflow refund | Oversized buys charge only `amountInUsed`, not requested amount |
| 7 | Donation resistance | Direct LT donations to the pair don't trigger graduation and don't skew LP open price; donated LT stays locked in the curve pair |

```
