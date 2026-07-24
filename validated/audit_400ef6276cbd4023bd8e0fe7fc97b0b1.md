Looking at the specific claim: that `get_vec` in `near/omni-prover/evm-prover/src/lib.rs` at line 237 can be used to force a cross-contract failure after state is partially updated.

**Tracing the full execution path:**

**Step 1 — `get_vec` location and role:**

`get_vec` is a private helper called only inside `_verify_trie_proof`, which is called from `verify_trie_proof`, which is called from `verify_proof` on the evm-prover contract. [1](#0-0) 

**Step 2 — When does `get_vec` execute relative to state changes?**

`verify_proof` on the prover runs entirely before the bridge contract's `fin_transfer_callback` is invoked. The prover contract itself has **no mutable state** — it is stateless (`EvmProver` only stores `light_client` and `chain_kind`, neither of which is modified during proof verification). [2](#0-1) 

The bridge's state changes (`add_fin_transfer`, `unlock_tokens_if_needed`, `remove_fast_transfer`) only happen inside `fin_transfer_callback` → `process_fin_transfer_to_near`, which is called **after** the prover promise resolves successfully. [3](#0-2) 

**Step 3 — What happens if `get_vec` panics?**

If `get_vec` panics (e.g., due to malformed RLP proof nodes), the prover's `verify_proof` call fails. The bridge's `fin_transfer_callback` receives a failed promise result at index 0 and immediately panics with `BridgeError::InvalidProofMessage` — **before any bridge state is touched**. [4](#0-3) 

**Step 4 — Can the attacker mutate non-signed envelope fields to reach `get_vec` with a valid proof but malformed trie nodes?**

The `EvmProof` struct contains `proof: Vec<Vec<u8>>` (the trie nodes), which are not signed. An attacker could submit malformed trie nodes. However, the trie proof is verified against `header.receipts_root`, which is part of the block header whose hash is verified against the light client. Malformed trie nodes would cause `verify_trie_proof` to return an empty vec (or panic), and the comparison `evm_proof.receipt_data != data` would fail, returning `Err(ProverError::InvalidProof)` — again before any state change.
<cite repo="Alyssadaypin/

### Citations

**File:** near/omni-prover/evm-prover/src/lib.rs (L30-35)
```rust
#[near(contract_state)]
#[derive(PanicOnDefault)]
pub struct EvmProver {
    pub light_client: AccountId,
    pub chain_kind: ChainKind,
}
```

**File:** near/omni-prover/evm-prover/src/lib.rs (L235-239)
```rust
/// Get element at position `pos` from rlp encoded data,
/// and decode it as vector of bytes
fn get_vec(data: &Rlp, pos: usize) -> Vec<u8> {
    data.at(pos).unwrap().as_val::<Vec<u8>>().unwrap()
}
```

**File:** near/omni-bridge/src/lib.rs (L709-711)
```rust
        let Ok(ProverResult::InitTransfer(init_transfer)) = Self::decode_prover_result(0) else {
            env::panic_str(BridgeError::InvalidProofMessage.to_string().as_str())
        };
```

**File:** near/omni-bridge/src/lib.rs (L1880-1890)
```rust
        let mut required_balance = self.add_fin_transfer(&transfer_message.get_transfer_id());

        let token = self.get_token_id(&transfer_message.token);
        let fast_transfer = FastTransfer::from_transfer(transfer_message.clone(), token.clone());
        let fast_transfer_status = self.get_fast_transfer_status(&fast_transfer.id());

        let lock_actions = vec![self.unlock_tokens_if_needed(
            transfer_message.get_origin_chain(),
            &token,
            transfer_message.amount.0,
        )];
```
