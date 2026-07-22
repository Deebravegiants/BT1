### Title
Value-Based `ValidResourceBounds` Type Determination in Protobuf Deserialization Causes Transaction Hash Mismatch Between Proposer and Validator - (File: `crates/apollo_protobuf/src/converters/transaction.rs`)

---

### Summary

The `TryFrom<protobuf::ResourceBounds> for ValidResourceBounds` implementation infers the `ValidResourceBounds` variant from the **values** of `l1_data_gas` and `l2_gas` (zero-check) rather than from an explicit type discriminant. This is the direct Sequencer analog of the `timestampAt` bug class: type is determined by value rather than by a tag. Because `get_tip_resource_bounds_hash` includes `l1_data_gas` in the hash only for `AllResources`, a transaction that enters the mempool as `AllResources{l1_data_gas=0, l2_gas=0}` receives a different hash at the gateway (H1, `AllResources` formula) than the hash the validator re-computes after protobuf round-trip (H2, `L1Gas` formula). The resulting `PartialBlockHash` mismatch causes every proposal containing such a transaction to fail `ProposalFin` comparison, and the validator executes the transaction under the wrong hash, causing `__validate__` to fail.

---

### Finding Description

**Root cause — value-based type determination in protobuf deserialization:**

In `crates/apollo_protobuf/src/converters/transaction.rs` lines 431–435, the protobuf-to-Rust conversion for `ValidResourceBounds` uses a zero-check on the decoded values to select the variant:

```rust
Ok(if l1_data_gas.is_zero() && l2_gas.is_zero() {
    ValidResourceBounds::L1Gas(l1_gas)
} else {
    ValidResourceBounds::AllResources(AllResourceBounds { l1_gas, l2_gas, l1_data_gas })
})
``` [1](#0-0) 

The JSON deserialization path (`ValidResourceBounds::deserialize` → `TryFrom<DeprecatedResourceBoundsMapping>`) uses a **different rule**: if the `L1_DATA_GAS` key is **present** in the map (even with zero value), it creates `AllResources`:

```rust
match resource_bounds_mapping.0.get(&Resource::L1DataGas) {
    Some(data_bounds) => Ok(Self::AllResources(AllResourceBounds {
        l1_gas: *l1_bounds,
        l1_data_gas: *data_bounds,
        l2_gas: *l2_bounds,
    })),
    None => {
        if l2_bounds.is_zero() { Ok(Self::L1Gas(*l1_bounds)) } else { Err(...) }
    }
}
``` [2](#0-1) 

A user can therefore submit a V3 transaction with `"L1_DATA_GAS": {"max_amount": "0x0", "max_price_per_unit": "0x0"}` in the JSON body. The gateway deserializes it as `AllResources{l1_data_gas=0, l2_gas=0}`.

**Hash divergence:**

`get_tip_resource_bounds_hash` branches on the variant:

```rust
resource_felts.extend(match resource_bounds {
    ValidResourceBounds::L1Gas(_) => vec![],
    ValidResourceBounds::AllResources(all_resources) => {
        vec![get_concat_resource(&all_resources.l1_data_gas, L1_DATA_GAS)?]
    }
});
``` [3](#0-2) 

`get_concat_resource` encodes the resource-name bytes (`L1_DATA_GAS`) into the felt even when the bounds are zero:

```rust
let concat_bytes =
    [[0_u8].as_slice(), resource_name.as_slice(), max_amount.as_slice(), max_price.as_slice()]
        .concat();
``` [4](#0-3) 

So `get_concat_resource(&zero, L1_DATA_GAS) ≠ 0`, and:

- **H1** (gateway, `AllResources`): `Poseidon(tip, l1_gas_concat, l2_gas_concat, l1_data_gas_concat)`
- **H2** (validator after protobuf round-trip, `L1Gas`): `Poseidon(tip, l1_gas_concat, l2_gas_concat)`

**H1 ≠ H2.**

**Attack path:**

1. User submits an invoke V3 transaction with `L1_DATA_GAS=0` in the JSON resource bounds.
2. Gateway deserializes as `AllResources`, computes H1, stores in mempool with `tx_hash = H1`.
3. Proposer pulls transaction from mempool, executes it with `tx_hash = H1`, builds `PartialBlockHash` from H1 via `prepare_txs_hashing_data`. [5](#0-4) 

4. Proposer serializes transaction to protobuf (`transaction_hash: None` — the hash is not transmitted). [6](#0-5) 

5. Validator deserializes protobuf: `l1_data_gas.is_zero() && l2_gas.is_zero()` → `L1Gas`.
6. Validator calls `convert_consensus_tx_to_internal_consensus_tx` → `convert_rpc_tx_to_internal` → `calculate_transaction_hash` → H2. [7](#0-6) 

7. Validator's batcher executes transaction with `tx_hash = H2`; account `__validate__` receives H2 but the user signed over H1 → signature verification fails → transaction reverted.
8. Validator builds `PartialBlockHash` from H2 ≠ H1.
9. `validate_proposal` compares `built_block` (H2-based) with `received_fin.proposal_commitment` (H1-based):

```rust
if built_block != received_fin.proposal_commitment {
    CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
    return Err(ValidateProposalError::ProposalFinMismatch);
}
``` [8](#0-7) 

→ Proposal rejected.

---

### Impact Explanation

- **Transaction hash binding is wrong**: the validator binds H2 to the transaction while the proposer bound H1. This is a direct match for "transaction conversion or signature/hash logic binds the wrong hash."
- **Wrong revert result**: the validator executes the transaction under H2, causing `__validate__` to fail with a signature error that would not occur under H1.
- **Consensus failure**: every proposal containing such a transaction is rejected by all validators, forcing repeated round changes. An attacker who keeps such transactions in the mempool can sustain the disruption across rounds.

---

### Likelihood Explanation

Any unprivileged user can submit a V3 transaction with `L1_DATA_GAS=0` through the standard RPC `add_invoke_transaction` endpoint. The gateway accepts it (it is a valid transaction format per `TryFrom<DeprecatedResourceBoundsMapping>`). No special privileges, network access, or validator keys are required. The attacker only needs to know the JSON transaction format.

---

### Recommendation

Replace the value-based zero-check in `TryFrom<protobuf::ResourceBounds> for ValidResourceBounds` with an explicit type discriminant:

1. **Add a type field to the protobuf `ResourceBounds` message** to explicitly encode the variant (`L1Gas` vs `AllResources`). The serializer sets it from the Rust variant; the deserializer reads it directly.
2. **Align the protobuf conversion with the JSON deserialization rule**: if `l1_data_gas` was explicitly set in the protobuf (field present, not defaulted), create `AllResources`; otherwise create `L1Gas`. This requires distinguishing "field absent" from "field present with zero value" in the protobuf schema (proto3 `optional` or a wrapper type).
3. **At minimum, normalize at the gateway**: before computing the hash, convert `AllResources{l1_data_gas=0, l2_gas=0}` to `L1Gas` so both paths agree. This is the lowest-risk short-term fix.

---

### Proof of Concept

```json
POST /gateway/add_transaction
{
  "type": "INVOKE_FUNCTION",
  "version": "0x3",
  "sender_address": "0x<account>",
  "calldata": ["..."],
  "signature": ["..."],
  "nonce": "0x0",
  "resource_bounds": {
    "L1_GAS":      {"max_amount": "0x100", "max_price_per_unit": "0x100"},
    "L2_GAS":      {"max_amount": "0x0",   "max_price_per_unit": "0x0"},
    "L1_DATA_GAS": {"max_amount": "0x0",   "max_price_per_unit": "0x0"}
  },
  "tip": "0x0",
  "paymaster_data": [],
  "account_deployment_data": [],
  "nonce_data_availability_mode": 0,
  "fee_data_availability_mode": 0
}
```

Gateway accepts the transaction. `TryFrom<DeprecatedResourceBoundsMapping>` sees `L1_DATA_GAS` present → `AllResources`. Hash H1 is computed with `l1_data_gas_concat` in the chain.

When the proposer includes it in a block and streams it over consensus, the validator's `TryFrom<protobuf::ResourceBounds>` sees `l1_data_gas.is_zero() && l2_gas.is_zero()` → `L1Gas`. Hash H2 is computed without `l1_data_gas_concat`.

```
H1 = Poseidon(INVOKE, ver, sender,
      Poseidon(tip, l1_gas_concat, l2_gas_concat, l1_data_gas_concat),
      paymaster_hash, chain_id, nonce, da_mode, deploy_data_hash, calldata_hash)

H2 = Poseidon(INVOKE, ver, sender,
      Poseidon(tip, l1_gas_concat, l2_gas_concat),   // l1_data_gas_concat absent
      paymaster_hash, chain_id, nonce, da_mode, deploy_data_hash, calldata_hash)

H1 ≠ H2  (l1_data_gas_concat = get_concat_resource(&zero, L1_DATA_GAS) ≠ 0)
```

Proposer's `ProposalCommitment` is derived from H1; validator's from H2. `ProposalFin` comparison fails → proposal rejected → consensus stall.

### Citations

**File:** crates/apollo_protobuf/src/converters/transaction.rs (L417-437)
```rust
impl TryFrom<protobuf::ResourceBounds> for ValidResourceBounds {
    type Error = ProtobufConversionError;
    fn try_from(value: protobuf::ResourceBounds) -> Result<Self, Self::Error> {
        let Some(l1_gas) = value.l1_gas else {
            return Err(missing("ResourceBounds::l1_gas"));
        };
        let Some(l2_gas) = value.l2_gas else {
            return Err(missing("ResourceBounds::l2_gas"));
        };
        // TODO(Shahak): Assert data gas is not none once we remove support for 0.13.2.
        let l1_data_gas = value.l1_data_gas.unwrap_or_default();
        let l1_gas: ResourceBounds = l1_gas.try_into()?;
        let l2_gas: ResourceBounds = l2_gas.try_into()?;
        let l1_data_gas: ResourceBounds = l1_data_gas.try_into()?;
        Ok(if l1_data_gas.is_zero() && l2_gas.is_zero() {
            ValidResourceBounds::L1Gas(l1_gas)
        } else {
            ValidResourceBounds::AllResources(AllResourceBounds { l1_gas, l2_gas, l1_data_gas })
        })
    }
}
```

**File:** crates/apollo_protobuf/src/converters/transaction.rs (L998-1025)
```rust
impl From<ConsensusTransaction> for protobuf::ConsensusTransaction {
    fn from(value: ConsensusTransaction) -> Self {
        match value {
            ConsensusTransaction::RpcTransaction(RpcTransaction::Declare(
                RpcDeclareTransaction::V3(txn),
            )) => protobuf::ConsensusTransaction {
                txn: Some(protobuf::consensus_transaction::Txn::DeclareV3(txn.into())),
                transaction_hash: None,
            },
            ConsensusTransaction::RpcTransaction(RpcTransaction::DeployAccount(
                RpcDeployAccountTransaction::V3(txn),
            )) => protobuf::ConsensusTransaction {
                txn: Some(protobuf::consensus_transaction::Txn::DeployAccountV3(txn.into())),
                transaction_hash: None,
            },
            ConsensusTransaction::RpcTransaction(RpcTransaction::Invoke(
                RpcInvokeTransaction::V3(txn),
            )) => protobuf::ConsensusTransaction {
                txn: Some(protobuf::consensus_transaction::Txn::InvokeV3(txn.into())),
                transaction_hash: None,
            },
            ConsensusTransaction::L1Handler(txn) => protobuf::ConsensusTransaction {
                txn: Some(protobuf::consensus_transaction::Txn::L1Handler(txn.into())),
                transaction_hash: None,
            },
        }
    }
}
```

**File:** crates/starknet_api/src/transaction/fields.rs (L575-606)
```rust
impl TryFrom<DeprecatedResourceBoundsMapping> for ValidResourceBounds {
    type Error = StarknetApiError;
    fn try_from(
        resource_bounds_mapping: DeprecatedResourceBoundsMapping,
    ) -> Result<Self, Self::Error> {
        if let (Some(l1_bounds), Some(l2_bounds)) = (
            resource_bounds_mapping.0.get(&Resource::L1Gas),
            resource_bounds_mapping.0.get(&Resource::L2Gas),
        ) {
            match resource_bounds_mapping.0.get(&Resource::L1DataGas) {
                Some(data_bounds) => Ok(Self::AllResources(AllResourceBounds {
                    l1_gas: *l1_bounds,
                    l1_data_gas: *data_bounds,
                    l2_gas: *l2_bounds,
                })),
                None => {
                    if l2_bounds.is_zero() {
                        Ok(Self::L1Gas(*l1_bounds))
                    } else {
                        Err(StarknetApiError::InvalidResourceMappingInitializer(format!(
                            "Missing data gas bounds but L2 gas bound is not zero: \
                             {resource_bounds_mapping:?}",
                        )))
                    }
                }
            }
        } else {
            Err(StarknetApiError::InvalidResourceMappingInitializer(format!(
                "{resource_bounds_mapping:?}",
            )))
        }
    }
```

**File:** crates/starknet_api/src/transaction_hash.rs (L202-211)
```rust
    // For new V3 txs, need to also hash the data gas bounds.
    resource_felts.extend(match resource_bounds {
        ValidResourceBounds::L1Gas(_) => vec![],
        ValidResourceBounds::AllResources(all_resources) => {
            vec![get_concat_resource(&all_resources.l1_data_gas, L1_DATA_GAS)?]
        }
    });

    Ok(HashChain::new().chain(&tip.0.into()).chain_iter(resource_felts.iter()).get_poseidon_hash())
}
```

**File:** crates/starknet_api/src/transaction_hash.rs (L216-226)
```rust
fn get_concat_resource(
    resource_bounds: &ResourceBounds,
    resource_name: &ResourceName,
) -> Result<Felt, StarknetApiError> {
    let max_amount = resource_bounds.max_amount.0.to_be_bytes();
    let max_price = resource_bounds.max_price_per_unit.0.to_be_bytes();
    let concat_bytes =
        [[0_u8].as_slice(), resource_name.as_slice(), max_amount.as_slice(), max_price.as_slice()]
            .concat();
    Ok(Felt::from_bytes_be(&concat_bytes.try_into().expect("Expect 32 bytes")))
}
```

**File:** crates/apollo_batcher/src/block_builder.rs (L230-244)
```rust
fn prepare_txs_hashing_data(
    transactions: &IndexMap<
        TransactionHash,
        (TransactionExecutionInfo, Option<TransactionSignature>),
    >,
) -> Vec<TransactionHashingData> {
    transactions
        .iter()
        .map(|(hash, (info, optional_signature))| TransactionHashingData {
            transaction_hash: *hash,
            transaction_output: info.output_for_hashing(),
            transaction_signature: optional_signature.clone().unwrap_or_default(),
        })
        .collect()
}
```

**File:** crates/apollo_transaction_converter/src/transaction_converter.rs (L388-393)
```rust
                )
            }
        };
        let tx_hash = tx_without_hash.calculate_transaction_hash(&self.chain_id)?;
        Ok((InternalRpcTransaction { tx: tx_without_hash, tx_hash }, proof_data))
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L244-249)
```rust
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }

    Ok(built_block)
```
