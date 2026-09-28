### Title
Tokens sent directly to the pool or controller (or left undeclared during `flash_position`) are permanently locked — neither contract has any withdrawal or recovery path — (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
The `InfiltrationPeriphery` bug class — a contract that can hold value but exposes no way to withdraw it — maps directly onto XOXNO Lending's `Controller` and `LiquidityPool`. Both contracts custody real token balances, yet neither exports a permissionless or even owner-gated token recovery. Any unprivileged user who transfers tokens directly to either address, or whose `flash_position` receiver delivers a token not declared in `collaterals`/`refund_assets`, loses those funds permanently.

### Finding Description
The controller's entrypoint surface (`contracts/controller/src/lib.rs`) contains no sweep, rescue, or generic token-transfer function; every outbound token movement is tied to a book entry (supply shares, debt repayment, refund of a measured delta). The pool is the same: all of its mutators are `#[only_owner]` (the controller) and every `transfer` out is driven by a cash-book mutation — there is no function that pays out unbooked token balance (`contracts/pool/src/lib.rs:99-252`).

Two concrete loss paths exist for an unprivileged address:

1. **Direct token transfer.** The threat model itself states "Direct donations do not rewrite those books" (`docs/explanation/threat-model.md`), and the pool explicitly notes "Cash is an accounting book, separate from the token balance" (`contracts/pool/src/lib.rs:34-36`). A token sent straight to the pool or controller raises the token balance but creates no shares, no cash entry, and no claimable claim — the excess can never leave because every `transfer_out` is bounded by booked amounts.

2. **`flash_position` undeclared asset.** In `process_flash_position`, the controller snapshots balances only for the declared `collaterals` and `refund_assets` (`flash_position.rs:125-130`), deposits positive deltas only for declared collaterals (`collect_collateral_deposits`, lines 325-352), and refunds only listed `refund_assets` (`refund_listed_assets`, lines 372-384). A receiver callback that sends any other token to the controller leaves it stranded: per the skill docs, "An undeclared token left on the controller is neither deposited nor refunded." The call still succeeds, so the loss is silent.

### Impact Explanation
Permanent freezing of funds. Tokens held by the controller or pool above what the books recognize are unrecoverable by any entrypoint — there is no owner `sweep`/`rescue` (contrast `swap-aggregator`'s `sweep_balance`, which the router does have but the pool/controller do not). For direct sends to the pool, the unbooked excess only ever offsets future shortfalls; for the controller, undeclared callback receipts are permanently stranded. The victim is the sender; no authorization beyond a plain token `transfer` is needed.

### Likelihood Explanation
Requires user error or a poorly written receiver — a mistaken `token.transfer(user, controller, amount)`, or a custom `FlashPositionReceiver` that returns collateral in a token not listed in `collaterals`/`refund_assets`. Same likelihood profile as the source report (accidental sends to a payable contract). Medium.

### Recommendation
- Add an owner-only `sweep`/`rescue` on both the controller and the pool that transfers out only the *unbooked* excess (pool: `token.balance(pool) - total booked cash across markets`; controller: any balance not owed to an in-flight flow — simplest is to allow sweeping only tokens with zero tracked obligation).
- Alternatively/additionally, in `process_flash_position`, treat any positive controller balance delta in a listed-but-undeclared asset as an implicit refund, or revert (`InvalidFlashloanReceiver`-style) when the receiver leaves residual tokens behind.

### Proof of Concept
```rust
// Path A: direct donation — succeeds, funds unrecoverable.
let token = token::Client::new(&env, &usdc);
token.transfer(&alice, &pool_address, &1_000_000);
// No controller or pool entrypoint can ever return this amount:
// pool cash book is unchanged, no shares minted, no sweep exists.

// Path B: undeclared token via flash_position.
// Receiver's execute_flash_position sends token X (listed in the hub but
// absent from `collaterals` and `refund_assets`) to the controller.
controller.flash_position(
    caller, 0, spoke_id, PositionMode::Multiply,
    debt_key, amount, receiver, data,
    collaterals,        // does not contain X
    refund_assets,      // does not contain X
);
// Call succeeds; balance delta of X on the controller is never measured,
// deposited, or refunded — locked forever.
```