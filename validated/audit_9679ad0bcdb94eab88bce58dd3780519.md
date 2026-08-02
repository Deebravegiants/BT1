### Title
`usdk::transfer_from` signed-approval nonce never advances, enabling unlimited signature replay to drain approved balances - (File: `aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move`)

### Summary
The `usdk` managed-stablecoin example implements an ERC20-`permit`-style delegated transfer, `transfer_from`, that lets a `spender` move funds out of an `owner`'s primary fungible store using an off-chain signed `Approval` message instead of the owner's on-chain signer. The message's replay-protection field, `nonce`, is populated with `account::get_sequence_number(from)` — the **live** sequence number of the owner's account — rather than a dedicated, monotonically-incrementing counter that this module owns and advances after each successful transfer. Because `transfer_from` is submitted and signed by `spender`, not by `from`, executing it never changes `from`'s account sequence number. The exact same signed `Approval` blob therefore continues to satisfy `account::verify_signed_message` on every subsequent call, letting the spender replay it and withdraw `amount` again and again until the owner happens to send an unrelated transaction of their own.

### Finding Description
`transfer_from` (`aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move:162-188`) reconstructs the expected signed message as:
```
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
primary_fungible_store::transfer_with_ref(transfer_ref, from, to, amount);
``` [1](#0-0) 

`account::get_sequence_number` is a pure read of the `Account.sequence_number` field. That field is only incremented by the Aptos VM when `from` itself is the transaction sender. Here, the transaction sender is `spender`, and the module never calls anything that bumps `from`'s sequence number nor stores a used-nonce set keyed by the signed message. Consequently:

1. The owner signs one `Approval{owner, to, nonce=N, amount}` message off-chain, intending to authorize a single transfer of `amount`.
2. `spender` submits `transfer_from` with that signature; it succeeds because `get_sequence_number(from) == N`.
3. `from`'s sequence number is still `N` after this call (it wasn't `from`'s transaction).
4. `spender` resubmits the identical signature in a new transaction; `get_sequence_number(from)` is still `N`, so `verify_signed_message` succeeds again, and `transfer_with_ref` moves another `amount` out of `from`'s primary store, bypassing the `frozen` flag via the `TransferRef` (`fungible_asset.move:1109-1117`, `primary_fungible_store.move:270-280`).
5. This repeats — draining up to the owner's entire balance — until the owner happens to submit any ordinary transaction from their own account, which is the only event that advances their sequence number.

The custody invariant broken is: an owner's fungible-asset transfer authorization must be single-use (or bounded), and the corresponding custody-control primitive (`TransferRef`) must not be exercisable more times than the owner explicitly authorized. Here the replay-protection nonce is decoupled from the actual action being authorized, so it protects nothing in the caller-initiated (spender-initiated) flow.

### Impact Explanation
This is a custody-grade theft primitive: it allows an unprivileged, arbitrary `spender` to withdraw a fungible asset balance from an `owner`'s primary store repeatedly beyond the single amount the owner authorized, using `TransferRef`-backed calls that ignore the `frozen`/denylist state (`fungible_asset::withdraw_with_ref` bypasses normal frozen checks; denylist enforcement here only re-checks `is_frozen`, not "already used"). Because `transfer_with_ref` operates on `Object<FungibleStore>` values tied to real token custody, an attacker holding one valid signed approval can extract far more value than the signer intended — effectively unbounded repeated theft limited only by the victim's balance and by how long it takes the victim to submit an unrelated transaction.

### Likelihood Explanation
High. No special privilege is required by `spender` beyond having received (or intercepted) one legitimately-signed `Approval` message for any amount — the exact same off-chain-signing workflow the module's own documentation instructs users to use. No additional signature or owner action is needed to replay it; the attacker simply resubmits the same call. This is trivially automatable and does not depend on network timing/front-running, unlike the original Solidity report — it can be exploited at leisure any time before the victim's next self-initiated transaction.

### Recommendation
Do not derive the `Approval` nonce from `account::get_sequence_number`. Maintain a dedicated per-owner counter (or used-signature set) inside `usdk`'s own state (e.g., a `Table<address, u64>` of next-expected-nonce, or a `Table<vector<u8>, bool>` of consumed signature hashes) that `transfer_from` increments/marks atomically before/after a successful `verify_signed_message` + `transfer_with_ref`, so each signed approval can only ever be consumed once. Optionally also bind an expiration timestamp into the signed message.

### Proof of Concept
1. Owner `from` (balance 1,000 USDK) signs an `Approval{owner: from, to: spender_or_third_party, nonce: N, amount: 100}` off-chain, intending to allow one 100-token transfer, where `N = account::get_sequence_number(from)` at signing time.
2. `spender` calls `usdk::transfer_from(spender, proof, from, scheme, pubkey, to, 100)`. It succeeds; `from`'s balance is now 900. `from`'s on-chain sequence number is unchanged (still `N`) because `from` did not sign/submit this transaction.
3. `spender` calls `usdk::transfer_from` again with the identical `proof`/arguments. `account::get_sequence_number(from)` is still `N`, so `verify_signed_message` succeeds again, and another 100 tokens are transferred. Balance is now 800.
4. Repeat step 3 up to 9 more times (or until `from` submits any unrelated transaction, bumping their sequence number) to drain the full 1,000 tokens from a single 100-token authorization.

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
