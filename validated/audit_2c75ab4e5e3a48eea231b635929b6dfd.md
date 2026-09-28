### Title
`Controller::withdraw` and `Controller::borrow` `to` recipient can be set to an address the user does not control, permanently losing the withdrawn/borrowed funds - ([File: contracts/controller/src/positions/supply.rs])

### Summary
The XOXNO Lending controller exposes an optional `to: Option<Address>` recipient on `withdraw` (and identically on `borrow`). The position's supply shares are burned and the underlying tokens are transferred to whatever address is passed. If the caller supplies an address they do not control (typo, wrong chain address, contract with no recovery path), the collateral position is destroyed while the tokens land in an inaccessible wallet — the funds are unrecoverable, matching the bug class of the external `SolverVault::requestWithdraw` report.

### Finding Description
In `process_withdraw`, the caller's authorization is checked against the account (`require_owner_or_delegate`), then the recipient is taken verbatim:

```rust
let recipient = to.unwrap_or_else(|| caller.clone());
```

The only validation applied is `require_external_recipient`, which rejects the pool and the controller itself (added under GH-17, tested in `tests/test-harness/tests/controller/recipient_is_protocol_contract.rs`), but nothing else. The pool-side leg `ops::withdraw::apply` then burns the supply shares and calls `cache.transfer_out(receiver, net_transfer)` directly to that arbitrary address. The same pattern exists in `borrow`, where debt is minted onto the account while proceeds go to `to`. The third-party payout path is intentional (the harness test `test_withdraw_to_pays_third_party_recipient` exercises paying Bob from Alice's withdrawal), so the protocol cannot distinguish a deliberate third-party payment from a fat-fingered or inaccessible address. There is no confirmation step, no `require_auth` on the recipient, and no mechanism to reclaim tokens once transferred on Soroban.

### Impact Explanation
Permanent freezing/loss of user funds: the account's supply position (or newly minted debt obligation) is consumed and the tokens are transferred to an address the user cannot access. Unlike the external report, there is no pending-request queue where a caretaker could intervene — settlement is atomic and irreversible within a single transaction.

### Likelihood Explanation
Medium: the mistake requires user error (wrong `to`), but the blast radius is total for the withdrawn/borrowed amount, and the API actively encourages passing `to` for delegate/third-party flows. Any integration constructing `to` programmatically (vaults, routers) that miscomputes the address loses the entire position in one call.

### Recommendation
Mirror the external fix where feasible:
- For `withdraw`, consider dropping the `to` parameter (or restricting it to the account owner), forcing funds back to the owner; third-party payout can be done by the owner after receipt.
- If `to` must be kept, require `recipient.require_auth()` when `recipient != caller`, so the receiving address provably consents and cannot be a dead address the sender mistyped — an auth check both proves the address is controllable and prevents sending to the protocol's own contracts generically.
- At minimum, extend the recipient guard to a broader denylist or require recipient auth on all recipient-override paths (`withdraw`, `borrow`).

### Proof of Concept
1. Alice supplies 10,000 USDC via `Controller::supply`, creating `account_id`.
2. Alice calls `Controller::withdraw(caller=alice, account_id, [(USDC, 0)], to=Some(bob_or_dead_address))` — amount `0` withdraws the entire position.
3. `process_withdraw` authenticates Alice, resolves `recipient` to the provided address, `settle_withdraw` → `apply_withdraw_batch` → `pool::ops::withdraw::apply` burns all of Alice's supply shares and calls `cache.transfer_out(recipient, net)`.
4. Alice's position reads 0; the tokens sit at an address Alice cannot control. No pause flag, error, or refund path exists. The same applies to `borrow(..., to=Some(wrong))`, which additionally leaves Alice holding the debt.