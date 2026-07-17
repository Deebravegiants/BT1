### Title
`DelegateAction` Signed Payload Lacks Chain Domain Separator — Cross-Chain Replay of Meta-Transactions - (File: core/primitives/src/action/delegate.rs)

### Summary
`DelegateAction` (NEP-366 meta-transaction) and `DelegateActionV2` (NEP-611 gas-key variant) are signed using a digest that commits to the action payload and a NEP discriminant, but never to the chain identity (`chain_id` or genesis hash). An unprivileged attacker who observes a valid `SignedDelegateAction` on one NEAR network (e.g., testnet) can replay it verbatim on another network (e.g., mainnet) whenever the signer's account, key, and nonce state are identical on both chains — a realistic condition for developers and validators who reuse keys across networks.

### Finding Description

`DelegateAction::get_nep461_hash()` constructs the signed digest as:

```rust
// core/primitives/src/action/delegate.rs, line 353-357
pub fn get_nep461_hash(&self) -> CryptoHash {
    let signable = SignableMessage::new(&self, SignableMessageType::DelegateAction);
    let bytes = borsh::to_vec(&signable).expect("Failed to deserialize");
    hash(&bytes)
}
```

`SignableMessage` prepends a 4-byte NEP discriminant (value `2^30 + 366 = 1073742230` for `DelegateAction`, `2^30 + 611` for `DelegateActionV2`) and then borsh-serializes the action body. The signed tuple is therefore:

```
hash( discriminant || sender_id || receiver_id || actions || nonce || max_block_height || public_key )
```

No `chain_id`, genesis hash, or any other network-scoping field is included. The `SignableMessage` scheme in `core/primitives/src/signable_message.rs` was designed to prevent a delegate action from being misread as a regular transaction (via the discriminant range), but it provides no cross-network domain separation. [1](#0-0) [2](#0-1) 

The verification path in `SignedDelegateAction::verify()` and `VersionedSignedDelegateAction::verify()` calls `get_nep461_hash()` and checks the signature against the signer's public key. No chain identity is checked at any point in the verification:

```rust
// core/primitives/src/action/delegate.rs, line 84-90
pub fn verify(&self) -> bool {
    let delegate_action = &self.delegate_action;
    let hash = delegate_action.get_nep461_hash();
    let public_key = &delegate_action.public_key;
    self.signature.verify(hash.as_ref(), public_key)
}
``` [3](#0-2) [4](#0-3) 

The runtime applies the delegate action in `apply_delegate_action` after calling `signed_delegate_action.verify()`. The only chain-sensitive checks are: (a) the nonce must exceed the on-chain access-key nonce, and (b) `max_block_height` must be ≥ current block height. Neither is chain-scoped. [5](#0-4) 

By contrast, regular `SignedTransaction` is implicitly chain-bound because it carries a `block_hash` that must reference a recent block on the target chain. `DelegateAction` has no equivalent binding — `max_block_height` is a plain integer, not a chain-specific hash.

### Impact Explanation

An attacker who observes a valid `SignedDelegateAction` on network A can submit it to network B via any relayer. If the signer's account exists on network B with the same access key and a matching (or lower) nonce, the runtime on network B will accept the signature and execute the inner actions — `Transfer`, `FunctionCall`, `AddKey`, `DeleteKey`, etc. — as if the signer had authorized them on network B. The corrupted protocol value is the **account balance and access-key nonce** on network B: tokens are transferred or keys are modified without the account owner's intent for that network.

### Likelihood Explanation

The preconditions are realistic:
- Developers routinely create accounts with the same name and key pair on both mainnet and testnet.
- Validators and infrastructure operators frequently reuse signing keys across networks.
- The nonce on network B must be ≤ the nonce embedded in the captured action. Because nonces start at 0 and increment, a freshly created account on network B satisfies this automatically.
- `max_block_height` must still be valid on network B. Since testnet and mainnet block heights are in the same order of magnitude and `max_block_height` is typically set far in the future, this window is wide.

An attacker needs only to monitor the public RPC or mempool of network A for `SignedDelegateAction` payloads and submit them to network B's RPC — no special privileges required.

### Recommendation

Include the chain identity in the signed payload. The minimal fix is to fold `chain_id` (or the genesis hash, which is already available as `GenesisId`) into the `SignableMessage` or into `DelegateAction` itself before hashing. Concretely, `get_nep461_hash` should hash `(discriminant, chain_id_or_genesis_hash, delegate_action_body)`. This mirrors how EIP-712 mandates `chainId` in the domain separator and how the `PartialEncodedStateWitness` uses a `signature_differentiator` string to prevent cross-version replay. [6](#0-5) 

### Proof of Concept

1. Alice has account `alice.near` on both mainnet and testnet, with the same ED25519 key and nonce `0` on mainnet.
2. Alice signs a `DelegateAction` on testnet: transfer 10 NEAR from `alice.near` to `attacker.near`, nonce=1, `max_block_height=200000000`.
3. The relayer broadcasts the meta-transaction on testnet; the `SignedDelegateAction` is visible in the mempool or on-chain.
4. Attacker extracts the borsh-encoded `SignedDelegateAction` and wraps it in a fresh mainnet `SignedTransaction` (signed by the attacker's own key) targeting `alice.near` as receiver, with the `DelegateAction` as the action payload.
5. Attacker submits this transaction to mainnet RPC via `broadcast_tx_commit`.
6. Mainnet runtime calls `apply_delegate_action` → `signed_delegate_action.verify()` → `get_nep461_hash()`. The hash is identical to the testnet hash (no chain_id in the digest). Signature verifies. Nonce 1 > 0 (mainnet nonce). `max_block_height` is valid. The transfer of 10 NEAR executes on mainnet, draining Alice's mainnet balance without her consent. [7](#0-6) [8](#0-7)

### Citations

**File:** core/primitives/src/action/delegate.rs (L70-96)
```rust
    Deserialize,
    PartialEq,
    Eq,
    Clone,
    Debug,
    ProtocolSchema,
)]
#[cfg_attr(feature = "schemars", derive(schemars::JsonSchema))]
pub struct SignedDelegateAction {
    pub delegate_action: DelegateAction,
    pub signature: Signature,
}

impl SignedDelegateAction {
    pub fn verify(&self) -> bool {
        let delegate_action = &self.delegate_action;
        let hash = delegate_action.get_nep461_hash();
        let public_key = &delegate_action.public_key;

        self.signature.verify(hash.as_ref(), public_key)
    }

    pub fn sign(singer: &Signer, delegate_action: DelegateAction) -> Self {
        let signature = singer.sign(delegate_action.get_nep461_hash().as_bytes());
        Self { delegate_action, signature }
    }
}
```

**File:** core/primitives/src/action/delegate.rs (L210-214)
```rust
impl VersionedSignedDelegateAction {
    pub fn verify(&self) -> bool {
        let hash = self.delegate_action.get_nep461_hash();
        self.signature.verify(hash.as_ref(), self.delegate_action.public_key())
    }
```

**File:** core/primitives/src/action/delegate.rs (L353-357)
```rust
    pub fn get_nep461_hash(&self) -> CryptoHash {
        let signable = SignableMessage::new(&self, SignableMessageType::DelegateAction);
        let bytes = borsh::to_vec(&signable).expect("Failed to deserialize");
        hash(&bytes)
    }
```

**File:** core/primitives/src/signable_message.rs (L18-25)
```rust
const MIN_ON_CHAIN_DISCRIMINANT: u32 = 1 << 30;
const MAX_ON_CHAIN_DISCRIMINANT: u32 = (1 << 31) - 1;
const MIN_OFF_CHAIN_DISCRIMINANT: u32 = 1 << 31;
const MAX_OFF_CHAIN_DISCRIMINANT: u32 = u32::MAX;

// NEPs currently included in the scheme
const NEP_366_META_TRANSACTIONS: u32 = 366;
const NEP_611_GAS_KEYS: u32 = 611;
```

**File:** core/primitives/src/signable_message.rs (L97-108)
```rust
impl<'a, T: BorshSerialize> SignableMessage<'a, T> {
    pub fn new(msg: &'a T, ty: SignableMessageType) -> Self {
        let discriminant = ty.into();
        Self { discriminant, msg }
    }

    pub fn sign(&self, signer: &Signer) -> Signature {
        let bytes = borsh::to_vec(&self).expect("Failed to deserialize");
        let hash = hash(&bytes);
        signer.sign(hash.as_bytes())
    }
}
```

**File:** runtime/runtime/src/actions.rs (L1281-1320)
```rust
    #[test]
    fn test_delegate_action() {
        let mut result = ActionResult::default();
        let (action_receipt, signed_delegate_action) = create_delegate_action_receipt();
        let sender_id = signed_delegate_action.delegate_action.sender_id.clone();
        let sender_pub_key = signed_delegate_action.delegate_action.public_key.clone();
        let access_key = AccessKey { nonce: 19000000, permission: AccessKeyPermission::FullAccess };

        let apply_state =
            create_apply_state(signed_delegate_action.delegate_action.max_block_height);
        let mut state_update = setup_account(&sender_id, &sender_pub_key, &access_key);

        apply_delegate_action(
            &mut state_update,
            &apply_state,
            &VersionedActionReceipt::from(&action_receipt),
            &sender_id,
            (&signed_delegate_action).into(),
            &mut result,
        )
        .expect("Expect ok");

        assert!(result.result.is_ok(), "Result error: {:?}", result.result.err());
        assert_eq!(
            result.new_receipts,
            vec![Receipt::V0(ReceiptV0 {
                predecessor_id: sender_id.clone(),
                receiver_id: signed_delegate_action.delegate_action.receiver_id.clone(),
                receipt_id: CryptoHash::default(),
                receipt: ReceiptEnum::Action(ActionReceipt {
                    signer_id: action_receipt.signer_id.clone(),
                    signer_public_key: action_receipt.signer_public_key.clone(),
                    gas_price: action_receipt.gas_price,
                    output_data_receivers: Vec::new(),
                    input_data_ids: Vec::new(),
                    actions: signed_delegate_action.delegate_action.get_actions(),
                }),
            })]
        );
    }
```

**File:** core/primitives/src/stateless_validation/partial_witness.rs (L94-122)
```rust
pub struct PartialEncodedStateWitnessInner {
    epoch_id: EpochId,
    shard_id: ShardId,
    height_created: BlockHeight,
    part_ord: usize,
    part: Box<[u8]>,
    encoded_length: usize,
    signature_differentiator: SignatureDifferentiator,
}

impl PartialEncodedStateWitnessInner {
    fn new(
        epoch_id: EpochId,
        chunk_header: ShardChunkHeader,
        part_ord: usize,
        part: Vec<u8>,
        encoded_length: usize,
    ) -> Self {
        Self {
            epoch_id,
            shard_id: chunk_header.shard_id(),
            height_created: chunk_header.height_created(),
            part_ord,
            part: part.into_boxed_slice(),
            encoded_length,
            signature_differentiator: "PartialEncodedStateWitness".to_owned(),
        }
    }
}
```
