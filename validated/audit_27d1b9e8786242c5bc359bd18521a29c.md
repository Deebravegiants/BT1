## Finding: `usdk::transfer_from` nonce reuse enables unlimited replay of a single owner-signed approval

### Title
Unbounded replay of a single signed `transfer_from` approval due to reuse of the account's on-chain sequence number as a nonce - (File: `aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move`)

### Summary
The external report's bug class is "a stale/second approval can be exploited because the authorization state is not properly invalidated between uses." The closest Aptos-native custodial analog is not the core `fungible_asset`/`primary_fungible_store` allowance-free transfer model (which has no persistent allowance concept at all), but the example stablecoin's off-chain-signed `transfer_from` mechanism in [1](#0-0) , which reimplements an ERC20-`transferFrom`-like flow using a signed `Approval` message.

### Finding Description
`transfer_from` builds an `Approval{owner, to, nonce, chain_id, spender, amount}` message where `nonce` is set to `account::get_sequence_number(from)` [2](#0-1) , and verifies the `spender`-supplied `proof` against this message via `account::verify_signed_message`. If the signature checks out, it immediately moves `amount` from `from`'s primary store to `to`'s primary store using the module's `TransferRef` [3](#0-2) .

The account sequence number returned by `account::get_sequence_number(addr)` only increases when `addr` itself is the transaction *sender* (i.e., when the owning account submits and pays for a transaction). It is **not** incremented by `transfer_from`, because in that call the transaction sender/signer is `spender`, not `from`. There is also no separate on-chain nonce-tracking or "used approval" set maintained by the `usdk` module itself — the only replay protection is the sequence-number-derived nonce baked into the signed message.

Consequently, once a token owner signs a single `Approval` message off-chain for a given `spender`/`amount`/`nonce`, that exact signature remains valid for every subsequent `transfer_from` call as long as `from`'s on-chain sequence number does not change. Since `from` typically does not submit transactions concurrently with the spender's usage of the approval, the `spender` can call `transfer_from` repeatedly with the identical `proof`, draining `from`'s balance in `amount`-sized increments over and over — not merely front-running a value change (as in the ERC20 case), but fully replaying a single authorization an unbounded number of times.

This breaks the custody invariant that an authorization for a fixed `amount` should be consumable at most once: the corrupted state is the recipient's/attacker's balance being inflated by multiple withdrawals against a single owner-authorized `amount`, and the owner's `FungibleStore` balance being drained beyond the intended single transfer.

### Impact Explanation
This is a direct, unprivileged theft-of-funds path against `usdk`-style fungible assets built on this pattern: any party holding one valid `Approval` signature and proof can drain the signer's entire available balance (up to however many times `amount` fits) without further owner consent, simply by resubmitting `transfer_from`. This matches the "Custody Impact Gate" criterion of theft of fungible-asset value via corrupted custody accounting (repeated unauthorized withdrawal against a single owner authorization).

### Likelihood Explanation
Likelihood is high wherever this example pattern is deployed as-is: the vulnerable path requires no special privilege — any account that obtains a valid signed `Approval` (e.g., as the intended one-time spender) can trivially resubmit the same call multiple times. The `from` account would have to send its own transaction to bump its sequence number to invalidate the message, which most token holders would not do proactively after signing a single off-chain approval.

### Recommendation
Do not derive the anti-replay nonce from `account::get_sequence_number`, since it is controlled by the owner's own transaction activity and is unrelated to consumption of this specific authorization. Instead, maintain a persistent, module-owned nonce or "used approval" mapping (e.g., a monotonically increasing per-owner counter stored in a resource under the metadata object, incremented atomically inside `transfer_from`), and require the signed message to include and consume that nonce so each signed approval can be redeemed exactly once. Additionally consider following OpenZeppelin/Lido-style single-use or explicitly decrementing allowance semantics for any allowance-like primitive that gets added to this or similar modules, and emit an event/approval-consumed marker to make replay externally observable.

### Proof of Concept
1. `from` account currently has sequence number `N` and signs an `Approval{owner: from, to, nonce: N, chain_id, spender, amount}` message, handing the signature (`proof`) to `spender`.
2. `spender` calls `usdk::transfer_from(spender, proof, from, scheme, pubkey, to, amount)`. `account::get_sequence_number(from)` still equals `N` because this transaction is signed by `spender`, not `from`; verification succeeds; `amount` is transferred from `from`'s store to `to`'s store [4](#0-3) .
3. Because `from` has not submitted any transaction of its own, `account::get_sequence_number(from)` is still `N`. `spender` calls `transfer_from` again with the identical `proof`/parameters; the check passes again and another `amount` is withdrawn from `from`'s store.
4. Step 3 repeats until `from`'s balance is exhausted or `from` finally submits a transaction (bumping its sequence number to `N+1`, which only prevents *future* reuse, not the drains already performed).

### Uncertainty
I was unable to directly view the body of `account::get_sequence_number` and `account::verify_signed_message` in `aptos-move/framework/aptos-framework/sources/account/account.move` in this session (tool budget exhausted before the file read completed), so the exact signature-scheme verification details (e.g., whether it internally binds to anything beyond the message contents) are based on the well-documented Aptos account model rather than a direct code read. I recommend confirming the body of these two functions before treating this as fully verified.

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
