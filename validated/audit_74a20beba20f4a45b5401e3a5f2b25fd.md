### Title
No Minimum Finality Enforcement in `verify_foreign_transaction` Allows MPC Attestation of Unfinalized Foreign-Chain Transactions - (File: crates/contract/src/lib.rs)

### Summary
The `verify_foreign_transaction` contract method accepts caller-supplied finality parameters (`EvmFinality::Latest`, `SolanaFinality::Processed`, `BlockConfirmations(0)`) without enforcing any minimum safety floor. The MPC network will produce a valid threshold signature attesting to a foreign-chain transaction that has not reached sufficient finality, enabling double-spend attacks against bridge contracts that rely on these attestations.

### Finding Description

`verify_foreign_transaction` performs the following checks before enqueuing a signing request:

1. Domain purpose is `ForeignTx`
2. Sufficient gas attachment
3. Minimum deposit (1 yoctoNEAR)
4. Chain is in the supported-chains set [1](#0-0) 

There is **no validation** of the finality parameters embedded in the `ForeignChainRpcRequest`. The `EvmFinality` enum exposes `Latest` as a fully accepted variant: [2](#0-1) 

`BlockConfirmations` is a plain `u64` with no minimum enforced at the type or contract level: [3](#0-2) 

The ABI schema confirms `"minimum": 0.0` for `BlockConfirmations`, meaning `0` is a valid on-chain input. [4](#0-3) 

On the node side, the EVM inspector's finality check with `Latest` simply verifies that the latest block number is ≥ the receipt's block number — a condition that is trivially satisfied for any transaction included in any block, including the most recent one that has not yet been finalized or made safe: [5](#0-4) 

For Bitcoin, the inspector's confirmation check is `block_confirmations_threshold <= transaction_block_confirmation`. With threshold `0`, this is always true: [6](#0-5) 

The signed payload encodes the request (including the caller-supplied finality parameter) verbatim: [7](#0-6) 

`respond_verify_foreign_tx` only validates the ECDSA signature against the root public key; it does not re-examine finality parameters: [8](#0-7) 

### Impact Explanation

The primary use case for `verify_foreign_transaction` is the Omnibridge inbound flow: a bridge contract on NEAR releases funds only after receiving an MPC-signed attestation that a foreign-chain deposit transaction finalized. If the MPC network signs attestations for transactions at `EvmFinality::Latest` (or `BlockConfirmations(0)` for Bitcoin), an attacker can:

1. Broadcast a deposit transaction on an EVM chain (e.g., Polygon, BNB, Arbitrum).
2. Immediately call `verify_foreign_transaction` with `EvmFinality::Latest` once the transaction appears in any block.
3. Receive a valid MPC threshold signature attesting to the transaction.
4. Submit the attestation to the NEAR bridge contract and withdraw funds.
5. Reorganize the EVM chain (feasible on chains with weaker finality guarantees) or use RBF/mempool replacement on Bitcoin to reverse the original deposit.

The signed attestation remains cryptographically valid even after the underlying transaction is reversed, enabling a double-spend. This matches the **High** impact category: forged foreign-chain verification that causes invalid bridge execution or double-spend conditions.

### Likelihood Explanation

Any unprivileged NEAR account can call `verify_foreign_transaction` with `EvmFinality::Latest`. The attacker does not need any special role or threshold collusion. The only external requirement is the ability to reorganize the target chain, which is non-trivial for Ethereum mainnet but realistic for Polygon, BNB, Arbitrum, and other supported EVM chains that have experienced reorgs historically. For Bitcoin, `BlockConfirmations(0)` combined with RBF-enabled transactions provides a mempool-level double-spend vector.

### Recommendation

1. **Enforce a minimum finality floor in `verify_foreign_transaction`**: Reject requests with `EvmFinality::Latest` (and optionally `EvmFinality::Safe`) for bridge-critical domains. Only `EvmFinality::Finalized` should be accepted for `ForeignTx` domain requests, or make the minimum finality level a per-chain governance parameter voted in alongside the RPC whitelist.
2. **Enforce a minimum `BlockConfirmations` value**: Reject `BlockConfirmations(0)` at the contract level. A governance-voted per-chain minimum (e.g., 6 for Bitcoin) should be stored in the on-chain RPC whitelist (`ChainEntry`) and enforced in `verify_foreign_transaction`.
3. **Cross-validate finality parameters against the on-chain RPC whitelist**: The `ChainEntry` voted in by operators is the natural place to store minimum finality requirements, analogous to the RPC quorum already planned there.

### Proof of Concept

An unprivileged caller submits:

```json
{
  "request": {
    "request": {
      "Polygon": {
        "tx_id": "<attacker_deposit_tx_hash>",
        "extractors": ["BlockHash"],
        "finality": "Latest"
      }
    },
    "domain_id": <foreign_tx_domain_id>,
    "payload_version": 1
  }
}
```

The contract accepts this (chain is supported, deposit is 1 yoctoNEAR, gas is sufficient). MPC nodes query the Polygon RPC, find the transaction in the latest block, pass the finality check (`latest_block >= receipt_block`), pass the canonical-chain check, and produce a threshold signature. The attacker receives a valid `VerifyForeignTransactionResponse` with `payload_hash` and `signature`. They submit this to the NEAR bridge contract to withdraw funds, then trigger a Polygon chain reorganization to reverse the deposit transaction. The MPC attestation remains valid.

### Citations

**File:** crates/contract/src/lib.rs (L519-557)
```rust
    pub fn verify_foreign_transaction(&mut self, request: VerifyForeignTransactionRequestArgs) {
        log!(
            "verify_foreign_transaction: predecessor={:?}, request={:?}",
            env::predecessor_account_id(),
            request
        );

        self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::ForeignTx,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );

        let requested_chain = request.request.chain();
        let supported_chains = self.get_supported_foreign_chains();
        if !supported_chains.contains(&requested_chain) {
            env::panic_str(
                &InvalidParameters::ForeignChainNotSupported {
                    requested: requested_chain,
                }
                .to_string(),
            );
        }

        let callback_gas = Gas::from_tgas(
            self.config
                .return_signature_and_clean_state_on_success_call_tera_gas,
        );

        let request = args_into_verify_foreign_tx_request(request);
        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_VERIFY_FOREIGN_TX_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_verify_foreign_tx_request(request, id),
        );
    }
```

**File:** crates/contract/src/lib.rs (L718-747)
```rust
        let signature_is_valid = match (&response.signature, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");

                let payload_hash: [u8; 32] = response.payload_hash.0;

                // Check the signature is correct against the root public key
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    &payload_hash,
                    &secp_pk,
                )
                .is_ok()
            }
            (signature_response, public_key_requested) => {
                return Err(RespondError::SignatureSchemeMismatch {
                    mpc_scheme: Box::new(signature_response.clone()),
                    user_scheme: Box::new(public_key_requested),
                }
                .into());
            }
        };

        if !signature_is_valid {
            return Err(RespondError::InvalidSignature.into());
        }
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L69-105)
```rust
#[cfg(all(feature = "abi", not(target_arch = "wasm32")))]
impl schemars::JsonSchema for ForeignTxPayloadVersion {
    fn schema_name() -> String {
        u8::schema_name()
    }

    fn is_referenceable() -> bool {
        false
    }

    fn json_schema(generator: &mut schemars::r#gen::SchemaGenerator) -> schemars::schema::Schema {
        u8::json_schema(generator)
    }
}

#[derive(
    Debug,
    Clone,
    Eq,
    PartialEq,
    Ord,
    PartialOrd,
    Hash,
    Serialize,
    Deserialize,
    BorshSerialize,
    BorshDeserialize,
)]
#[cfg_attr(
    all(feature = "abi", not(target_arch = "wasm32")),
    derive(schemars::JsonSchema, borsh::BorshSchema)
)]
pub struct VerifyForeignTransactionRequestArgs {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L767-772)
```rust
#[non_exhaustive]
pub enum EvmFinality {
    Latest,
    Safe,
    Finalized,
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1262-1282)
```rust
#[derive(
    Debug,
    Clone,
    Eq,
    PartialEq,
    Ord,
    PartialOrd,
    Hash,
    Serialize,
    Deserialize,
    BorshSerialize,
    BorshDeserialize,
    derive_more::Into,
    derive_more::From,
    derive_more::AsRef,
)]
#[cfg_attr(
    all(feature = "abi", not(target_arch = "wasm32")),
    derive(schemars::JsonSchema, borsh::BorshSchema)
)]
pub struct BlockConfirmations(pub u64);
```

**File:** crates/contract/tests/snapshots/abi__abi_has_not_changed.snap (L2516-2520)
```text
        "BlockConfirmations": {
          "type": "integer",
          "format": "uint64",
          "minimum": 0.0
        },
```

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L100-125)
```rust
    /// Checks that the receipt's block has reached the requested finality level — i.e. that the
    /// head of the chain at `finality` is at or past `receipt_block_number`.
    async fn verify_finality_level(
        &self,
        receipt_block_number: U64,
        finality: EthereumFinality,
    ) -> Result<(), ForeignChainInspectionError> {
        let finality_tag = match finality {
            EthereumFinality::Finalized => FinalityTag::Finalized,
            EthereumFinality::Safe => FinalityTag::Safe,
            EthereumFinality::Latest => FinalityTag::Latest,
        };
        let args = GetBlockByNumberArgs::new(
            BlockNumberOrTag::Tag(finality_tag),
            ReturnFullTransactionObjects::from(false),
        );
        let head: GetBlockByNumberResponse = self
            .client
            .request(GET_BLOCK_BY_NUMBER_METHOD, &args)
            .await?;

        if head.number < receipt_block_number {
            return Err(ForeignChainInspectionError::NotFinalized);
        }
        Ok(())
    }
```

**File:** crates/foreign-chain-inspector/src/bitcoin/inspector.rs (L50-59)
```rust
        let transaction_block_confirmation = rpc_response.confirmations.into();
        let enough_block_confirmations =
            block_confirmations_threshold <= transaction_block_confirmation;

        if !enough_block_confirmations {
            return Err(ForeignChainInspectionError::NotEnoughBlockConfirmations {
                expected: block_confirmations_threshold,
                got: transaction_block_confirmation,
            });
        }
```
