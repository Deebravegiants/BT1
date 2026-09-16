### Title
Unvalidated `message.from` length causes a panic (DoS) in `pallet-hyper-fungible-token`'s calldata-execution origin derivation - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
In `on_accept`, when an incoming HFT transfer carries calldata (`message.data` non-empty) without a signature, the pallet derives the dispatch `origin` directly from the ABI-decoded `message.from` bytes without validating its length first, unlike every other length-sensitive field in the same function.

### Finding Description
`IsmpModule::on_accept` in `modules/pallets/hyper-fungible-token/src/module.rs` decodes the ABI body into a `Message { from, to, amount, data }` struct (`Message::abi_decode(&body)`, line 59). Every other length-sensitive conversion in this function validates length before touching memory:

- `to_bytes` (recipient) is checked for `len() == 32` or `== 20`, else `Err(HftError::InvalidRecipientLength(...))` (lines 63–71).
- The refund path in `on_timeout` (lines 224–230+) checks `from_bytes.len() == 32` / `== 20` before copying.

But the calldata-execution origin-derivation branch does not:

```rust
} else {
    let from_bytes = message.from.as_ref();
    if source.is_evm() {
        T::EvmToSubstrate::convert(H160::from_slice(
            &from_bytes[from_bytes.len() - 20..],
        ))
    } else {
        let mut account = [0u8; 32];
        account.copy_from_slice(from_bytes);
        account.into()
    }
};
```
(`modules/pallets/hyper-fungible-token/src/module.rs:176-186`)

`from_bytes.len() - 20` underflows (usize subtraction) whenever `from_bytes.len() < 20`, and `account.copy_from_slice(from_bytes)` panics whenever `from_bytes.len() != 32`. This mirrors the CVE-2026-23531 bug class: a size-derived byte range/copy is used against an untrusted-length buffer without validating the destination/source length first, causing an out-of-bounds access (here, a Rust panic/trap rather than a heap OOB, since Substrate/WASM execution traps on unchecked slice/arith operations).

### Impact Explanation
`message.from` is part of the ABI-decoded cross-chain `Message` body, distinct from the ISMP-authenticated `PostRequest.from`/`source` pair used only to look up `ContractToAsset`. Nothing in `on_accept` validates the length of the inner `message.from` field before this branch executes — it is trusted implicitly to always be produced correctly by the peer contract's `send()` logic (`abi.encodePacked(msg.sender)`), but the pallet performs no defensive length check on it, unlike the parallel `to`/refund paths that were hardened. If this invariant is ever violated (e.g., a peer contract admitted with different encoding conventions, a future SDK/contract change, or any code path where `from` isn't strictly `msg.sender`-sized), the runtime will panic/trap while processing an otherwise fully-verified, deliverable ISMP message, aborting the extrinsic's execution and repeating on every retry — a message a relayer cannot get past, an outright denial-of-service for that specific transfer + calldata-execution flow with no recovery besides a runtime upgrade.

### Likelihood Explanation
Low-to-medium under the *current* peer contract implementations (the only production encoders always emit a 20-byte or 32-byte `from`), but the check is missing at the exact point that determines dispatch origin for arbitrary runtime calls, and the pallet does not enforce the invariant itself — it relies entirely on distributed, external, chain-specific encoders staying correct forever. Any future peer, alternate implementation, or governance-added chain that encodes `from` incorrectly (even accidentally, not maliciously) turns into an unconditionally reachable panic for every relayer attempting to deliver that message.

### Recommendation
Add explicit length checks for `from_bytes` in the calldata-execution origin-derivation branch, mirroring the existing `to_bytes` (`InvalidRecipientLength`) and `on_timeout` refund-path validation, e.g.:
```rust
} else {
    let from_bytes = message.from.as_ref();
    if source.is_evm() {
        if from_bytes.len() != 20 {
            Err(HftError::InvalidSenderLength(from_bytes.len()))?;
        }
        T::EvmToSubstrate::convert(H160::from_slice(from_bytes))
    } else {
        if from_bytes.len() != 32 {
            Err(HftError::InvalidSenderLength(from_bytes.len()))?;
        }
        let mut account = [0u8; 32];
        account.copy_from_slice(from_bytes);
        account.into()
    }
};
```

### Proof of Concept
1. Construct a `PostRequest` whose `body` ABI-encodes `Message { from: <bytes of length != 20 (e.g. 5 or 0 bytes)>, to: <valid 20/32-byte recipient>, amount: <valid>, data: SubstrateCalldata { signature: None, runtime_call: <any valid call> }.encode() }`.
2. Register the sending `source`/`from` pair in `ContractToAsset` (this only requires that the *outer* `PostRequest.from`/`source` be a registered peer — the *inner* `message.from` field is unconstrained by this lookup).
3. Deliver via `handle_unsigned`/pallet-ismp so `on_accept` executes with `source.is_evm() == true` and the crafted inner `message.from` of length < 20.
4. `from_bytes.len() - 20` underflows in the `usize` subtraction, panicking the runtime (or, if `source.is_evm() == false` and `from_bytes.len() != 32`, `account.copy_from_slice(from_bytes)` panics directly) — reproducible deterministically by any party who can get the ABI body onto the wire, aborting delivery of that message every time it's retried.