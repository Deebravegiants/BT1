Found the exact analog. This is a genuine custody-grade replay bug in `usdk.move`'s `transfer_from`.

### Title
Repeatable fungible-asset `transfer_from` approval replay drains the owner's balance because the "nonce" is the owner's global transaction sequence number, not a per-approval or per-spender counter - (File: `aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move`)

### Summary
`usdk::transfer_from` lets a `spender` move funds out of `from`'s primary fungible-asset store using an off-chain signed `Approval` message. The approval's replay-protection field (`nonce`) is bound to `account::get_sequence_number(from)` at verification time, evaluated fresh on every call. As long as `from` does not submit any transaction of its own (a very common state for a custodial/cold or infrequently-active depositor account), this value never changes, so a single signed approval can be replayed an unlimited number of times by the `spender`, draining the store — exactly the class of bug in the referenced Community.sol `escrow` finding (authorization data reused because the replay-protection value never advances).

### Finding Description
`transfer_from` constructs the challenge and checks the signature like this: [1](#0-0) 

The `nonce` field of `Approval` is populated with `account::get_sequence_number(from)` — the account's on-chain transaction sequence number — not a dedicated, monotonically-incrementing "spend nonce" that is updated by `transfer_from` itself. There is no state written by `transfer_from` (no consumed-approval table, no incremented per-owner spend counter) that would invalidate the approval after use. `account::get_sequence_number` only advances when `from` itself sends a transaction from its own account; `transfer_from` is called and paid for by `spender`, not by `from`, so executing `transfer_from` never touches `from`'s sequence number.

Consequently, once `from` signs one `Approval{owner, to, nonce, chain_id, spender, amount}` message (e.g., to authorize a single $5 transfer while `from` is offline/custodial and has sequence number 7), `spender` can call `transfer_from` with the identical `proof` bytes as many times as `from`'s balance allows, because the recomputed `expected_message` will be byte-identical to what was signed, and `account::verify_signed_message` (`aptos-move/framework/aptos-framework/sources/account/account.move:1282-1320`) only checks the signature against the message content, not against any consumed/invalidated set.

This is structurally identical to the Community.sol `escrow` bug: the signed authorization is not bound to a value that is guaranteed to change as a direct result of consuming that specific authorization.

### Impact Explanation
Any account that delegates a spend approval to a `spender` via `transfer_from`, and does not immediately follow up with its own on-chain transaction, is exposed to unlimited draining of its entire USDK (fungible-asset) primary-store balance by that `spender`, using only the one signature the owner produced for a single, bounded transfer. This is direct theft of fungible-asset custody value (mint/burn framework example is intended to model a production-quality managed stablecoin), matching "Theft ... of ... fungible assets ... held value" in the custody impact gate. Custodial or automation-driven owner accounts (which frequently only ever receive funds and never submit their own transactions) are the most exposed, and the damage is bounded only by the owner's balance.

### Likelihood Explanation
High for any owner account that is not actively transacting from its own address at the time it authorizes a `transfer_from`. This is a common real-world pattern (e.g., a deposit/custody account that only receives assets and authorizes withdrawals via signed messages, without itself signing on-chain transactions). No special privileges are required by the attacker beyond being the named `spender`, and the same `proof`/message bytes are reusable without modification.

### Recommendation
Do not use the owner's global account sequence number as the replay-protection value for a value-transfer approval. Introduce an explicit per-owner (or per-owner/spender) monotonically increasing "approval nonce" stored in module state (e.g., in `State` or a new resource keyed by owner), require the signed `Approval.nonce` to match the stored value, and increment that stored value inside `transfer_from` after a successful transfer — mirroring the C4-recommended fix of adding an explicit `escrowNonce` field that is checked and incremented atomically with the balance-affecting operation, rather than relying on an ambient counter the function itself does not control.

### Proof of Concept
1. `from` (owner, sequence number `N`) approves a $5 transfer to `spender` by signing `Approval{owner: from, to, nonce: N, chain_id, spender, amount: 5}` and hands the signature to `spender` off-chain.
2. `from` never submits any of its own transactions afterward (its sequence number stays `N`).
3. `spender` calls `transfer_from(spender, proof, from, scheme, pubkey, to, 5)`. `account::get_sequence_number(from)` still returns `N`, so `expected_message` matches the signed `proof`, and 5 units are transferred.
4. `spender` calls `transfer_from` again with the identical `proof`/arguments. `from`'s sequence number is still `N` (transfer_from does not increment it), so the check passes again and another 5 units are transferred.
5. `spender` repeats step 4 until `from`'s entire balance is drained — using only the single signature obtained in step 1.

### Citations

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L162-188)
```text
    public fun transfer_from(
        spender: &signer,
        proof: vector<u8>,
        from: address,
        from_account_scheme: u8,
        from_public_key: vector<u8>,
        to: address,
        amount: u64,
    ) acquires Management, State {
        assert_not_paused();
        assert_not_denylisted(from);
        assert_not_denylisted(to);

        let expected_message = Approval {
            owner: from,
            to: to,
            nonce: account::get_sequence_number(from),
            chain_id: chain_id::get(),
            spender: signer::address_of(spender),
            amount,
        };
        account::verify_signed_message(from, from_account_scheme, from_public_key, proof, expected_message);

        let transfer_ref = &borrow_global<Management>(usdk_address()).transfer_ref;
        // Only use with_ref API for primary_fungible_store (PFS) transfers in this module.
        primary_fungible_store::transfer_with_ref(transfer_ref, from, to, amount);
    }
```
