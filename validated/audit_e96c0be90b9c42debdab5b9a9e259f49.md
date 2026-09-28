### Title
Frozen/disallowed RWA-token account owner bypasses the issuer gate by withdrawing collateral to an allowlisted third party - (File: contracts/controller/src/positions/supply.rs)

### Summary
The Ethena bug class: a restricted account escapes its restriction by routing the exit through a different address — the gate checks the caller and the transfer recipient but never the economic owner. In XOXNO Lending the same shape exists for issuer-gated collateral (e.g., the Liqvid `RwaGatedToken` market). `withdraw` accepts an arbitrary `to` recipient; the only recipient validation is `require_external_recipient`, which rejects the pool and controller. The RWA token's allowlist/freeze is enforced by the token contract on the `pool → to` transfer, so only `to` is gated. A frozen or de-allowlisted account owner keeps full ownership of the account NFT and can withdraw the entire collateral position to any allowlisted accomplice, who forwards the value off-chain.

### Finding Description
- `process_withdraw` (contracts/controller/src/positions/supply.rs:140-168) authenticates `caller` via `require_owner_or_delegate`, then sets `let recipient = to.unwrap_or_else(|| caller.clone())` and only calls `require_external_recipient(env, &mut cache, &recipient)` on it. No check ties the recipient to the owner, and no check asks whether the owner itself is eligible to hold the restricted asset — that eligibility is only enforced downstream, inside the token's `transfer(pool, recipient, amount)`.
- The harness proves the gate sits on the recipient, not the owner: in `lqv_issuer_pool_freeze_blocks_token_movement_until_unfrozen` and `lqv_pool_removed_from_allowlist_after_deposits_blocks_exits_only` (tests/test-harness/tests/controller/liqvid_rwa_collateral.rs:560-629), freezing/de-allowlisting the **pool** blocks exits, and in `lqv_a_frozen_borrower_is_still_liquidatable` freezing **alice** does not stop her position's collateral moving — because seizure/withdraw moves tokens from the pool, never from alice. The mirror-image case — frozen/disallowed alice, allowlisted recipient — is untested and unguarded.
- Endpoint reference confirms `withdraw(caller, account_id, withdrawals, to)` is NFT owner/delegate gated with `to` being a free `Option<Address>` (docs/reference/endpoints.md:26), matching the report's `redeem(shares, receiver, owner)` where `receiver` was free and `owner` unchecked.

### Impact Explanation
An issuer that freezes or de-allowlists a holder to stop them redeeming gated collateral (a compliance action) cannot actually confine the position: the restricted owner calls `withdraw` with `to = <allowlisted third party>` and the pool pays out in full. The restriction on the owner is fully bypassed with no protocol-level loss — consistent with the Ethena precedent, this is a Medium: a compliance/control break, not direct theft of other users' funds.

### Likelihood Explanation
Trivially reachable by any restricted account owner: the account NFT stays owned by the restricted user (freezing the token doesn't touch NFT ownership or `require_owner_or_delegate`), `withdraw` remains callable even under global pause, and one external allowlisted address is needed as the payout leg. A registered-manager delegate (`add_delegate` → delegate calls `withdraw` with `to = self`) achieves the same result through a second route.

### Recommendation
For issuer-gated collateral markets, bind the withdrawal recipient to an address that itself satisfies the gate — e.g., default `to` to the account owner, or have the controller reject `to` addresses the token reports as not allowed/frozen (an `allowed(to)`/`authorized(to)`-style precheck before `settle_withdraw`). Alternatively, restrict `to` on gated assets to `None`/owner so the token gate always sees the real beneficiary.

### Proof of Concept
Setup mirrors `liqvid_rwa_collateral.rs`: LIQVID market in its own hub/spoke, only the pool and `bob` allowlisted; `alice` holds an account with 10 LIQVID collateral.

```rust
// alice deposits while allowlisted, then issuer disallows/freezes alice
z.disallow(&alice);        // or z.token().freeze(&alice)

// bypass: alice withdraws her whole position to allowlisted bob
let paid = z.try_withdraw_to("alice", id, 0 /* zero = withdraw all */, Some(bob.clone()));
assert!(paid.is_ok(), "restriction bypassed: owner gate never consulted");
assert_eq!(z.liq_balance(&bob), 10, "full collateral paid to third party");
assert_eq!(z.units(id), 0);
```

This mirrors the report's `stakedUSDe.approve(56)` + `redeem(amount, 56, alice)` PoC: the restricted `owner` (`alice`) is never checked; only the recipient is gated.