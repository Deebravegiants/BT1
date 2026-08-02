### Title
`transfer_from` in the USDK stablecoin example relies on an unconsumed sequence-number "nonce," allowing a single signed transfer approval to be replayed indefinitely - ([File: aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move])

### Summary
The `usdk` module implements an ERC-2612/`permit`-style delegated transfer: an owner off-chain signs an `Approval { owner, to, nonce, chain_id, spender, amount }` message, and any `spender` can later submit `transfer_from` to move `amount` tokens out of `owner`'s primary store using `TransferRef`. The "nonce" used for replay protection is `account::get_sequence_number(from)` [1](#0-0) , i.e., the owner's on-chain account sequence number at verification time — but `transfer_from` never causes that sequence number to advance (the owner isn't the transaction sender, and nothing in the function increments or otherwise invalidates the signed message). The same signed `Approval` can therefore be submitted by `spender` over and over, each time transferring another `amount` out of `owner`'s primary store, until `owner`'s balance is exhausted or `owner` submits an unrelated transaction that happens to bump their sequence number.

### Finding Description
`transfer_from` builds the exact expected message from current on-chain state and checks the supplied signature against it: [2](#0-1) 

The `nonce` field is populated from `account::get_sequence_number(from)` at call time, not from any dedicated, single-use, incrementing counter owned by this module. Because the multisig/permit pattern's safety depends on the "approval" being consumed (invalidated) after first use — exactly the same custody invariant violated in the external `safeApprove()` report, where an authorization value must be reset/invalidated before it can be legitimately reused — this implementation never invalidates the authorization at all. `owner`'s account sequence number is a property of `owner`'s own transaction stream and is completely independent of `spender`'s call to `transfer_from`. As long as `owner` does not submit any other transaction, `get_sequence_number(from)` stays constant, so the identical `(proof, from_public_key, ...)` tuple continues to satisfy `account::verify_signed_message` on every subsequent call, and `primary_fungible_store::transfer_with_ref` moves another `amount` each time [3](#0-2) .

This breaks the fungible-asset custody invariant that a signed transfer authorization should move a bounded, single-use amount of the custody-held asset. `TransferRef` in this module is a privileged capability held by `Management` that can bypass `frozen` checks and move value directly [4](#0-3) , so the replay directly corrupts the account's balance/custody state, not just an event log.

### Impact Explanation
Any party that legitimately obtains one valid `Approval` signature for amount `X` (e.g., an intended one-time payment authorization to a merchant/spender) can drain up to the owner's full balance by resubmitting `transfer_from` with the same proof repeatedly, each time moving another `X` tokens, as long as the owner's sequence number does not change in between. This is a direct, unprivileged path to unauthorized fund transfer/theft of USDK-style stablecoin balances — a custody-grade, high-severity impact (potential total loss of owner funds beyond the intended, single approved transfer).

### Likelihood Explanation
Likelihood is high for any deployment that reuses this reference pattern as-is: the vulnerable code path (`transfer_from`) is a public entry-adjacent function requiring only a previously obtained valid signature (which the owner is expected to hand to the intended spender as normal usage) and no special privilege beyond being any signer able to submit a transaction. No additional race condition or timing constraint is required beyond "owner hasn't sent an unrelated transaction since signing," which is the common case for most wallets between approvals.

### Recommendation
Do not derive the anti-replay nonce from `account::get_sequence_number(from)`. Instead, maintain a dedicated per-owner (or per-approval) nonce/allowance resource inside the `usdk` module that is explicitly incremented/consumed atomically within `transfer_from` before or as part of the transfer, and reject any replayed nonce. Alternatively, adopt an explicit "approve-and-consume" allowance model (analogous to `safeApprove`'s recommended two-step reset), storing a remaining allowance per `(owner, spender)` pair, decremented on each `transfer_from` call, with the amount transferred never exceeding what remains — mirroring the fix pattern in the seed report of zeroing/consuming the authorization before it can be reused.

### Proof of Concept
1. `owner` signs one `Approval { owner, to: attacker_or_spender, nonce: account::get_sequence_number(owner), chain_id, spender, amount: X }` intending to authorize a single transfer of `X` USDK to `spender`.
2. `spender` calls `usdk::transfer_from(spender, proof, owner, scheme, pubkey, to, X)`. This succeeds: `X` tokens move from `owner`'s primary store to `to` [5](#0-4) .
3. `owner` has not submitted any other transaction, so `account::get_sequence_number(owner)` is unchanged.
4. `spender` calls `usdk::transfer_from` again with the exact same `proof`/parameters. `account::verify_signed_message` succeeds again because the recomputed `expected_message` (including `nonce`) is identical to the first call, and another `X` tokens are transferred.
5. Step 4 repeats until `owner`'s balance is exhausted, well beyond the single `X`-token authorization the owner believed they granted.

### Citations

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L160-188)
```text
    /// Allow a spender to transfer tokens from the owner's account given their signed approval.
    /// Caller needs to provide the from account's scheme and public key which can be gotten via the Aptos SDK.
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

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L1108-1117)
```text
    /// Transfer `amount` of the fungible asset with `TransferRef` even it is frozen.
    public fun transfer_with_ref<T: key>(
        self: &TransferRef,
        from: Object<T>,
        to: Object<T>,
        amount: u64
    ) acquires FungibleStore, ConcurrentFungibleBalance {
        let fa = self.withdraw_with_ref(from, amount);
        self.deposit_with_ref(to, fa);
    }
```
