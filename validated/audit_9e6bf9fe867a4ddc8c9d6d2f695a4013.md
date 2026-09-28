### Title
Stale delegate grants revive when the position NFT returns to the granting owner — `get_delegates` filters stale grants at lookup time but never removes them, so ownership changes fail to permanently drop the old grant (File: contracts/controller/src/storage/account.rs)

### Summary
The upstream bug class is "a lookup/acquire helper whose result must be paired with a release, and the missing release leaves stale state that is consumed again later" (`debugfs_lookup` without `dput`, fixed by `debugfs_lookup_and_remove`). The lending-side analog is the `DelegateGrant` entry keyed `ControllerKey::Delegates(account_id)`: it is *looked up and filtered* on every delegate read, but the ownership-change path never *removes* it. A grant stamped by owner A stays in storage while the NFT sits with owner B, and silently becomes valid again the moment the NFT is transferred back to A, because validity is tested only by comparing `grant.granted_by` to the *current* owner.

### Finding Description
`get_delegates` resolves delegates by loading the stored `DelegateGrant` and accepting it iff `grant.granted_by == *owner`, where `owner` is the *current* NFT holder:

- `contracts/controller/src/storage/account.rs:174-181` — `get_delegates` filters on `granted_by == owner` and returns the stored `Vec<Address>`; it does not delete a mismatched grant.
- `contracts/controller/src/storage/account.rs:185-199` — `set_delegates` removes the entry only when the list becomes empty through an explicit `remove_delegate` call.
- `contracts/controller/src/storage/account.rs:226-247` — `remove_delegate` deletes a stale grant (`grant.granted_by != *owner` → `persistent.remove`), and the comment explicitly states the reason: *"preventing those grants from reactivating if the NFT returns to their original owner."* So the codebase itself acknowledges the reactivation hazard — but the removal only happens if someone calls `remove_delegate` *while the NFT is in foreign hands*. `get_delegates`/`add_delegate` paths merely overwrite or ignore stale entries; nothing cleans the grant when the NFT moves (no delegate-clearing hook in the position-NFT `transfer`/`transfer_from` flow, per the position-NFT README's storage table and burn/transfer description).

The consequence: grant validity is a pure function of who holds the NFT *right now*. Sequence:

1. Owner A grants delegate D (`add_delegate` writes `DelegateGrant{granted_by: A, delegates: [D]}`).
2. A transfers the position NFT to B via `position-nft::transfer`. From B's perspective `granted_by (A) != owner (B)`, so D is inert — but the entry is still on disk.
3. Nobody calls `remove_delegate` in between (B cannot meaningfully remove "their" delegates because the grant isn't stamped by B; A no longer controls the account).
4. B transfers the NFT back to A (or A reacquires the same `account_id` via any path — e.g., an intermediate holder transfers it back, a marketplace round-trip, a liquidation wrapper, or simply A→B→A collateral shuffling between the user's own wallets where the grant was *intended* to die at step 2).
5. `get_delegates(account_id, A)` now returns `[D]` again — the stale grant reactivates with no fresh authorization from A.

This mirrors the kernel leak exactly: the `DelegateGrant` was "acquired" at grant time, the ownership transition was the point that should have released it (the missing `dput`), and the unreleased entry is later consumed by a subsequent lookup as if it were fresh.

### Impact Explanation
A delegate is a privileged actor on the account: the delegate list gates access to position-management entrypoints (supply/withdraw/borrow/repay/strategy operations executed "on behalf of" the account). An ex-delegate whose grant the owner implicitly revoked by moving the position away regains full delegate powers the instant the position returns — without any new `grant_delegate` call or owner signature. Depending on the delegate surface, this enables the ex-delegate to withdraw collateral, open borrows against the account's collateral, or drive flash/multiply strategies on the account — i.e., theft or manipulation of user funds enabled by state that should have been destroyed. Severity Medium: it requires the NFT to leave and return to the same owner, which is an ordinary pattern for users who move positions between their own wallets or through escrow/marketplace flows.

### Likelihood Explanation
Triggering requires only: (a) a pre-existing delegate grant, (b) an outbound NFT transfer, (c) the NFT returning to the original owner. No attacker control over contracts is needed — the *ex-delegate* is the attacker, and steps (b)–(c) are normal user behavior the attacker just waits for. The one mitigating factor is that a `remove_delegate` call by the interim owner — or anyone while the NFT is away — permanently deletes the stale grant, but nothing forces or incentivizes that call, and the common case (delegates simply forgotten after the transfer) leaves the landmine in place.

### Recommendation
Treat the delegate grant like the dentry: release it at the point ownership changes rather than filtering at read time. Options:

- Burn-on-transfer semantics: have the controller's position-NFT integration (or `account.rs` ownership resolution) clear `ControllerKey::Delegates(account_id)` whenever the resolved owner differs from `grant.granted_by` — i.e., make `get_delegates` delete a mismatched grant it observes (the `lookup_and_remove` fix), matching what `remove_delegate` already does for the explicit-call case.
- Alternatively, include a generation/epoch in the grant: store the NFT transfer count or a per-owner nonce in `AccountMeta`, and stamp grants with it, so a returning owner cannot match an old stamp.

### Proof of Concept
Conceptual trace on Soroban test env (`Env::default()` + `mock_all_auths`):

1. Deploy controller + position NFT; A opens account → `account_id = N`, NFT minted to A.
2. A calls `grant_delegate(A, D)` → `Delegates(N) = DelegateGrant{granted_by: A, delegates: [D]}`.
3. A calls `position_nft.transfer(A, B, N)`. Assert `env.as_contract(controller, || get_delegates(env, N, &B).is_empty())` — D correctly inert for B — *and* `env.storage().persistent().has(&ControllerKey::Delegates(N))` — the entry was never removed.
4. B calls `position_nft.transfer(B, A, N)` — NFT returns to A.
5. Assert `get_delegates(env, N, &A) == [D]` — the stale grant reactivated with no call from A. D can now invoke delegate-gated controller entrypoints against account N.

Step 3's `has(...)` assertion is the "leak" (unreleased lookup result); step 5 is the exploitable consequence.