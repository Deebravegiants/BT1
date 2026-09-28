I have limited iterations left; let me check the two likely analogs: stranded donations/locked funds paths and the liquidation/controller refund flow.### Title
Tokens transferred directly to the pool or controller are permanently locked with no recovery path - (File: contracts/pool/README.md)

### Summary
The bug class from the reference report is user-paid funds becoming locked inside a contract after a downstream operation fails or is never routed through the expected path, with no mechanism for users (or anyone) to reclaim them. In XOXNO Lending, any tokens sent directly to a `LiquidityPool` instance or to the controller — e.g., a user who repays by transferring to the pool address instead of calling `controller.repay`, a classic-asset airdrop, or a mistakenly prefunded `supply`/`repay`/`recapitalize` amount — become permanently locked. Neither contract exposes a sweep, skim, sync, or recovery entrypoint, and the pool's own accounting model guarantees the tokens can never leave through a legitimate path.

### Finding Description
The pool treats `cash` as a pure bookkeeping number and explicitly never reconciles it against the real `token.balance()` except via a strict-equality check inside `flash_loan` (`contracts/pool/README.md`, lines 56–63). Consequently:

- **No crediting path exists for unsolicited deposits.** `supply`, `repay` and `recapitalize` all credit `cash` "on the controller's word, without verifying the transfer" (`contracts/pool/README.md`, lines 58–63). A direct `token.transfer` to the pool raises the real balance but leaves `cash` unchanged, so the tokens belong to no market's book.
- **No exit path exists for the excess.** `withdraw`, `borrow`, `claim_revenue` and `flash_loan` payouts are all gated by `Cache::require_reserves`, which reads the `cash` book, not the token balance (`contracts/pool/tests/flows.rs`, lines 3404–3406). The donation is invisible to every book-driven payout, so no entrypoint will ever emit it.
- **No sweep exists.** A repo-wide search finds no `sweep`/`recover`/`rescue`/`skim` entrypoint in `contracts/pool` or `contracts/controller`. The only outbound token calls are the book-gated ops plus the `repay`/`recapitalize` refund legs, which refund an amount derived from a *declared inbound* payment — never the stranded custody itself.
- **Worse than a passive lock: the strict-equality check weaponizes it.** `flash_loan` checks `token.balance()` against expected book values three times with strict equality (`contracts/pool/README.md`, lines 34–36, 62–63). Any stray donation makes `balance > cash`, so `flash_loan` — and every controller entrypoint built on it — reverts permanently for that market.
- **The controller has the same hole.** `refund_controller_balance_delta` in `contracts/controller/src/payments.rs` (lines 39–52) refunds only the delta *since* a snapshot and deliberately "preserves the pre-existing balance". Any tokens sitting in the controller before a call — donations, a failed-strategy residue, prior stranded refunds — are untouched by every flow and there is no recovery function.

This mirrors the reference issue exactly: funds arrive at a contract through a legitimate-looking or off-path action, the contract has no `transferId`-style record or claim path, and the funds are unrecoverable.

### Impact Explanation
Permanent freezing of user funds (an accepted impact). Any user who sends tokens to the pool or controller address directly — a realistic mistake given that liquidation docs warn that "transferring repayment directly to the pool is a donation" (`skills/xoxno-lending-liquidations/SKILL.md`, lines 76–79) — loses them forever. As a secondary effect, a single-asset donation of any size permanently bricks `flash_loan` for that market, and through it the flash-dependent controller surface.

### Likelihood Explanation
Low-to-moderate for any individual user but certain in aggregate: the pool address is public, tokens on Stellar are plain SAC transfers, and the README explicitly documents that direct transfers are donations. The flash-loan strict-equality check additionally means a single griefer can permanently disable flash loans for a market by donating 1 stroop of that asset to the pool — an unprivileged, cheap, permissionless action.

### Recommendation
Add an owner-gated `sweep`/`skim` entrypoint on the pool that transfers `token.balance() − sum(cash across all markets)` to the owner (or revenue), so stranded deposits are recoverable; and/or change the `flash_loan` reconciliation to a `>=` check so excess custody does not permanently brick the market. Apply the equivalent recovery function on the controller for pre-existing balances that `refund_controller_balance_delta` intentionally skips.

### Proof of Concept
1. Deploy controller + pool, list a USDC market.
2. Any address calls `token.transfer(user, pool, amount)` — no auth on the pool side is required.
3. `get_reserves`/`state_snapshot` shows `cash` unchanged while `token.balance(pool)` increased by `amount`.
4. Iterate every outbound entrypoint (`withdraw`, `borrow`, `claim_revenue`, `flash_loan`, `repay`/`recapitalize` refunds via the controller): none can emit the donation because all are sized by the `cash` book.
5. `pool.flash_loan(...)` now panics on the strict `balance == expected` check regardless of the loan amount — the donation has permanently frozen the flash path with no recovery entrypoint.

Verified against: `contracts/pool/README.md` (lines 31–90, trust table and flash-loan reconciliation), `contracts/pool/src/ops/repay.rs` (lines 25–34, refund derived from declared amount), `contracts/pool/src/ops/recapitalize.rs` (lines 26–67, same pattern), `contracts/controller/src/payments.rs` (lines 39–52, pre-existing balance preserved), and `contracts/pool/tests/flows.rs` (lines 3376–3410, confirming custody can exceed the `cash` book with no book-driven way out). Caveat: I could not confirm within the iteration budget whether an undocumented owner-side recovery exists elsewhere; the visible ABI in `contracts/pool/README.md`'s surface table contains none.