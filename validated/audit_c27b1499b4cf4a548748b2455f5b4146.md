### Title
Missing Minimum Confirmation Count Enforcement in `verify_foreign_transaction` Allows Signing of Unconfirmed Bitcoin Transactions - (File: `crates/contract/src/lib.rs`)

### Summary

The `verify_foreign_transaction` contract method accepts a `BitcoinRpcRequest` with `confirmations: BlockConfirmations(0)` and performs no lower-bound validation on that field. Because the `BitcoinInspector` passes its confirmation check whenever `threshold <= actual_confirmations`, a threshold of zero is always satisfied — even for a transaction that has never been mined. Any unprivileged caller can therefore obtain a valid MPC threshold signature attesting to a Bitcoin transaction that has zero on-chain finality, enabling double-spend attacks against bridge contracts that rely on MPC signatures as finality proofs.

### Finding Description

**Root cause — no minimum confirmation count enforced at the contract layer**

`verify_foreign_transaction` in `crates/contract/src/lib.rs` (lines 519–557) validates only that the domain exists, the chain is supported, and the deposit is sufficient. It performs no validation on the `confirmations` field of `BitcoinRpcRequest`: [1](#0-0) 

The `BitcoinRpcRequest` struct in `crates/near-mpc-contract-interface/src/types/foreign_chain.rs` declares `confirmations` as a plain `u64` wrapper with no minimum: [2](#0-1) 

The ABI schema confirms `"minimum": 0.0` — zero is an accepted value: [3](#0-2) 

**Root cause — `BitcoinInspector` always passes when threshold is zero**

`BitcoinInspector::extract` in `crates/foreign-chain-inspector/src/bitcoin/inspector.rs` checks:

```rust
let enough_block_confirmations =
    block_confirmations_threshold <= transaction_block_confirmation;
```

When `block_confirmations_threshold = 0`, the inequality `0 <= N` is trivially true for any `N ≥ 0`, including a transaction that is still in the mempool (where `confirmations = 0`). The inspector proceeds to extract values and the MPC network signs the payload. [4](#0-3) 

**Exploit path**

1. Attacker broadcasts a Bitcoin transaction `T` to the bridge address.
2. Attacker immediately calls `verify_foreign_transaction` with `confirmations: BlockConfirmations(0)` and `tx_id = T`.
3. The contract enqueues the request without any bound check.
4. MPC nodes call `BitcoinInspector::extract`; the `0 <= actual_confirmations` check passes even if `T` is unconfirmed.
5. MPC nodes sign `ForeignTxSignPayloadV1 { request: BitcoinRpcRequest { confirmations: 0, … }, values: [BlockHash(…)] }`.
6. Attacker receives a valid threshold signature and submits it to the bridge contract to claim NEAR-side funds.
7. Attacker broadcasts a conflicting RBF transaction to reclaim the Bitcoin, completing the double-spend.

The design document explicitly states the feature is intended to let "NEAR contracts react to external chain events without a trusted relayer" and that "The request includes a bounded number of extractors" — implying bounds are a design requirement. The `confirmations` field is the finality bound for Bitcoin, yet it is left unbounded. [5](#0-4) 

### Impact Explanation

An unprivileged attacker can obtain a legitimate MPC threshold signature over a Bitcoin transaction that has never been confirmed. Any bridge contract that uses `verify_foreign_transaction` as its finality oracle and does not independently re-validate the `confirmations` field in the signed payload is vulnerable to a double-spend: the attacker claims bridge funds on NEAR while simultaneously invalidating the Bitcoin deposit via RBF or a competing transaction. This constitutes **forged foreign-chain verification causing double-spend conditions** — a High-severity impact under the allowed scope.

### Likelihood Explanation

The attack requires only a valid NEAR account and the 1 yoctoNEAR minimum deposit. No privileged access, no threshold collusion, and no cryptographic break are needed. The attacker controls the `confirmations` field directly in the public `verify_foreign_transaction` call. The attack is immediately executable on any supported Bitcoin domain.

### Recommendation

Enforce a protocol-level minimum confirmation count at the contract layer before enqueuing the request:

1. **Contract-level guard**: In `verify_foreign_transaction`, reject `BitcoinRpcRequest` with `confirmations == 0` (or below a configurable per-chain minimum stored in `ForeignChainConfiguration`).
2. **Governance-controlled minimum**: Add a `min_confirmations: BlockConfirmations` field to the on-chain `ForeignChainConfiguration` for Bitcoin. Governors vote on the minimum; the contract enforces it on every incoming request.
3. **Type-level enforcement**: Replace `pub confirmations: BlockConfirmations` with a `BoundedConfirmations` newtype that panics or errors on construction with a zero value, mirroring the `BoundedVec` pattern already used elsewhere in the codebase. [6](#0-5) 

### Proof of Concept

```rust
// Attacker submits verify_foreign_transaction with confirmations: 0
contract.verify_foreign_transaction(VerifyForeignTransactionRequestArgs {
    domain_id: foreign_tx_domain_id,
    payload_version: ForeignTxPayloadVersion::V1,
    request: ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest {
        tx_id: attacker_unconfirmed_tx_id,
        confirmations: BlockConfirmations(0), // ← no lower-bound check in contract
        extractors: vec![BitcoinExtractor::BlockHash],
    }),
});

// Inside BitcoinInspector::extract:
//   block_confirmations_threshold = 0
//   transaction_block_confirmation = 0  (tx is in mempool, not mined)
//   0 <= 0  →  true  →  check passes, values extracted, MPC signs
//
// Attacker receives a valid threshold signature for an unconfirmed transaction.
// Bridge contract releases NEAR-side funds.
// Attacker RBF-replaces the Bitcoin tx → double-spend complete.
``` [7](#0-6) [1](#0-0) [2](#0-1)

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L267-271)
```rust
pub struct BitcoinRpcRequest {
    pub tx_id: BitcoinTxId,
    pub confirmations: BlockConfirmations,
    pub extractors: Vec<BitcoinExtractor>,
}
```

**File:** crates/contract/tests/snapshots/abi__abi_has_not_changed.snap (L2516-2520)
```text
        "BlockConfirmations": {
          "type": "integer",
          "format": "uint64",
          "minimum": 0.0
        },
```

**File:** crates/foreign-chain-inspector/src/bitcoin/inspector.rs (L33-70)
```rust
    async fn extract(
        &self,
        transaction: BitcoinTransactionHash,
        block_confirmations_threshold: BlockConfirmations,
        extractors: Vec<BitcoinExtractor>,
    ) -> Result<Vec<BitcoinExtractedValue>, ForeignChainInspectionError> {
        let request_parameters = GetRawTransactionArgs {
            transaction_hash: TransportBitcoinTransactionHash::from(*transaction),
            verbose: VERBOSE_RESPONSE,
        };

        // TODO(#1978): add retry mechanism if the error from the request is transient
        let rpc_response: GetRawTransactionVerboseResponse = self
            .client
            .request(GET_RAW_TRANSACTION_METHOD, &request_parameters)
            .await?;

        let transaction_block_confirmation = rpc_response.confirmations.into();
        let enough_block_confirmations =
            block_confirmations_threshold <= transaction_block_confirmation;

        if !enough_block_confirmations {
            return Err(ForeignChainInspectionError::NotEnoughBlockConfirmations {
                expected: block_confirmations_threshold,
                got: transaction_block_confirmation,
            });
        }

        self.verify_block_is_canonical(rpc_response.blockhash)
            .await?;

        let extracted_values = extractors
            .iter()
            .map(|extractor| extractor.extract_value(&rpc_response))
            .collect();

        Ok(extracted_values)
    }
```

**File:** docs/foreign-chain-transactions.md (L19-30)
```markdown
At a high level:

1. A user submits a `verify_foreign_transaction` request with a chain-specific query and a list of **extractors**.
2. MPC nodes query the foreign chain via configured RPC providers.
3. Each node runs the requested extractors over the fetched RPC result(s), producing a **bounded set of small typed values**.
4. If extraction succeeds, MPC signs a canonical encoding of `(request, observed_values, observed_at)` and returns the signature on-chain.

This design intentionally keeps responses small and on-chain-friendly by enforcing:

* Each extractor returns **exactly one** typed value.
* The request includes a bounded number of extractors.
* Extracted values have strict size limits (e.g., bytes length caps).
```

**File:** crates/near-mpc-bounded-collections/src/bounded_vec.rs (L32-51)
```rust
/// BoundedVec errors
#[derive(Error, PartialEq, Eq, Debug, Clone)]
pub enum BoundedVecOutOfBounds {
    /// Items quantity is less than L (lower bound)
    #[error("Lower bound violation: got {got} (expected >= {lower_bound})")]
    LowerBoundError {
        /// L (lower bound)
        lower_bound: usize,
        /// provided value
        got: usize,
    },
    /// Items quantity is more than U (upper bound)
    #[error("Upper bound violation: got {got} (expected <= {upper_bound})")]
    UpperBoundError {
        /// U (upper bound)
        upper_bound: usize,
        /// provided value
        got: usize,
    },
}
```
