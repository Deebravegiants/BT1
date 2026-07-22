Let me trace the exact execution order in `add_tx` and the validation chain carefully.

The execution trace is unambiguous. Here is the exact call sequence that makes the exploit work:

**`add_tx` (lines 479–514):** [1](#0-0) 

Step 1 — `add_ready_declares()` fires **before** any validation. [2](#0-1) 

Step 2 — `add_ready_declares` pops D from `delayed_declares` and calls `add_tx_inner`, moving D into `tx_pool`. [3](#0-2) 

Step 3 — `validate_no_delayed_declare_front_run` checks **only** `delayed_declares`. D is no longer there, so the guard returns `Ok(())`. [4](#0-3) 

Step 4 — `validate_fee_escalation` then finds D in `tx_pool` via `get_by_address_and_nonce`, and if the invoke's fee clears `should_replace_tx`, returns `Some(D_reference)`. [5](#0-4) 

Step 5 — `remove_replaced_tx(D)` evicts D; the invoke is inserted. [6](#0-5) 

The existing test `no_delay_declare_front_run` only covers the case where the clock has **not** advanced past the delay — it never advances time, so D stays in `delayed_declares` and the guard fires correctly. The post-graduation window is completely untested. [7](#0-6) 

---

### Title
Declare-delay front-run protection bypassed at graduation: `add_ready_declares` moves declare to `tx_pool` before `validate_no_delayed_declare_front_run` executes — (`crates/apollo_mempool/src/mempool.rs`)

### Summary
`add_tx` calls `add_ready_declares()` unconditionally before running any admission validation. If the incoming invoke arrives at the exact moment a delayed declare's timer has expired, `add_ready_declares` graduates the declare from `delayed_declares` into `tx_pool`. The subsequent call to `validate_no_delayed_declare_front_run` only inspects `delayed_declares`, finds nothing, and returns `Ok`. Fee-escalation logic then finds the declare in `tx_pool` and evicts it, admitting the invoke in its place. The declared-class protection invariant is broken.

### Finding Description
In `add_tx` the ordering is:

```
add_ready_declares()          // graduates D: delayed_declares → tx_pool
add_tx_validations(invoke)    // validate_no_delayed_declare_front_run checks delayed_declares → empty → Ok
                              // validate_fee_escalation finds D in tx_pool → evicts D
```

`validate_no_delayed_declare_front_run` is documented as preventing "fee escalation to a declare that is being delayed," but it only queries `self.delayed_declares.contains(...)`. Once `add_ready_declares` has moved D to `tx_pool`, the guard is blind to it. The protection window is effectively zero at the graduation boundary. [4](#0-3) 

### Impact Explanation
A valid declare transaction is evicted from the mempool for a protocol-invalid reason (the delay-protection invariant is supposed to prevent exactly this replacement). The account's nonce=0 slot is then occupied by the invoke. The declare must be resubmitted, and if the invoke is sequenced first, the declare will be rejected with `NonceTooOld`. This is a **High** mempool-admission impact: a valid transaction is dropped and a replacement that the protection mechanism was designed to block is admitted.

### Likelihood Explanation
The attacker is the account owner (they must sign the invoke with the account's private key). The timing window is not a single-millisecond race: any `add_tx` call submitted after the declare's `submission_time + declare_delay` will trigger graduation. The attacker simply waits for the delay to expire, then submits the invoke. No privileged access is required beyond owning the account.

### Recommendation
Move `add_ready_declares()` to **after** `add_tx_validations`, or extend `validate_no_delayed_declare_front_run` to also check `tx_pool` for transactions that were originally declares (e.g., by tagging them at insertion time). The simplest fix is to swap the call order so that the guard runs against the pre-graduation state:

```rust
pub fn add_tx(&mut self, args: AddTransactionArgs) -> MempoolResult<()> {
    let mut account_nonce_updates = self.remove_expired_txs();
    // Validations first, THEN graduate ready declares.
    let tx_reference = TransactionReference::new(&args.tx);
    self.add_tx_validations(tx_reference, &args.tx, args.account_state.nonce)?;
    if !self.is_fifo() {
        self.add_ready_declares();
    }
    ...
}
```

### Proof of Concept
```rust
#[test]
fn delayed_declare_evicted_by_post_delay_fee_escalation() {
    let fake_clock = Arc::new(FakeClock::default());
    let declare_delay = Duration::from_secs(5);
    let mut mempool = Mempool::new(
        MempoolConfig {
            static_config: MempoolStaticConfig {
                declare_delay,
                enable_fee_escalation: true,
                fee_escalation_percentage: 0, // any higher fee qualifies
                ..Default::default()
            },
            ..Default::default()
        },
        fake_clock.clone(),
    );

    // Step 1: submit declare D at (address=0x0, nonce=0).
    let declare = declare_add_tx_input(declare_tx_args!(
        resource_bounds: valid_resource_bounds_for_testing(),
        sender_address: contract_address!("0x0"),
        tx_hash: tx_hash!(1)
    ));
    add_tx(&mut mempool, &declare);

    // Step 2: advance clock past declare_delay.
    fake_clock.advance(declare_delay + Duration::from_millis(1));

    // Step 3: submit invoke I at (address=0x0, nonce=0) with higher fee.
    // This add_tx call triggers add_ready_declares, graduating D to tx_pool,
    // then validate_no_delayed_declare_front_run misses D, and fee escalation evicts it.
    let invoke = add_tx_input!(
        tx_hash: 2, address: "0x0", tx_nonce: 0, account_nonce: 0,
        tip: 999, max_l2_gas_price: 999
    );
    // Expected: error (declare should be protected). Actual: Ok — declare is evicted.
    add_tx_expect_error(
        &mut mempool,
        &invoke,
        MempoolError::DuplicateNonce {
            address: contract_address!("0x0"),
            nonce: nonce!(0),
        },
    );
}
```

### Citations

**File:** crates/apollo_mempool/src/mempool.rs (L439-441)
```rust
        if let Some(existing_tx_reference) = replaced_tx_reference {
            self.remove_replaced_tx(existing_tx_reference);
        }
```

**File:** crates/apollo_mempool/src/mempool.rs (L479-488)
```rust
    pub fn add_tx(&mut self, args: AddTransactionArgs) -> MempoolResult<()> {
        // First remove old transactions from the pool.
        let mut account_nonce_updates = self.remove_expired_txs();
        if !self.is_fifo() {
            self.add_ready_declares();
        }

        let tx_reference = TransactionReference::new(&args.tx);
        self.add_tx_validations(tx_reference, &args.tx, args.account_state.nonce)
            .inspect_err(|err| self.log_add_tx_error(err, &args))?;
```

**File:** crates/apollo_mempool/src/mempool.rs (L619-630)
```rust
    fn add_ready_declares(&mut self) {
        let now = self.clock.now();
        while let Some((submission_time, _args)) = self.delayed_declares.front() {
            if now - self.config.static_config.declare_delay < *submission_time {
                break;
            }
            let (_submission_time, args) =
                self.delayed_declares.pop_front().expect("Delay declare should exist.");
            self.add_tx_inner(args);
        }
        self.update_state_metrics();
    }
```

**File:** crates/apollo_mempool/src/mempool.rs (L715-726)
```rust
    fn validate_no_delayed_declare_front_run(
        &self,
        tx_reference: TransactionReference,
    ) -> MempoolResult<()> {
        if self.delayed_declares.contains(tx_reference.address, tx_reference.nonce) {
            return Err(MempoolError::DuplicateNonce {
                address: tx_reference.address,
                nonce: tx_reference.nonce,
            });
        }
        Ok(())
    }
```

**File:** crates/apollo_mempool/src/mempool.rs (L776-791)
```rust
        let Some(existing_tx_reference) = self.tx_pool.get_by_address_and_nonce(address, nonce)
        else {
            // Replacement irrelevant: no existing transaction with the same nonce for address.
            return Ok(None);
        };

        if !self.should_replace_tx(&existing_tx_reference, &incoming_tx_reference) {
            info!(
                "{existing_tx_reference} was not replaced by {incoming_tx_reference} due to \
                 insufficient fee escalation."
            );
            // TODO(Elin): consider adding a more specific error type / message.
            return Err(MempoolError::DuplicateNonce { address, nonce });
        }

        Ok(Some(existing_tx_reference))
```

**File:** crates/apollo_mempool/src/fee_mempool_test.rs (L1436-1464)
```rust
#[rstest]
fn no_delay_declare_front_run() {
    // Create a mempool with a fake clock.
    let fake_clock = Arc::new(FakeClock::default());
    let mut mempool = Mempool::new(
        MempoolConfig {
            static_config: MempoolStaticConfig {
                declare_delay: Duration::from_secs(5),
                // Always accept fee escalation to test only the delayed declare duplicate nonce.
                enable_fee_escalation: true,
                fee_escalation_percentage: 0,
                ..Default::default()
            },
            ..Default::default()
        },
        fake_clock.clone(),
    );
    let declare = declare_add_tx_input(
        declare_tx_args!(resource_bounds: valid_resource_bounds_for_testing(), sender_address: contract_address!("0x0"), tx_hash: tx_hash!(0)),
    );
    add_tx(&mut mempool, &declare);

    let expected_error = MempoolError::DuplicateNonce {
        address: declare.tx.contract_address(),
        nonce: declare.tx.nonce(),
    };
    add_tx_expect_error(&mut mempool, &declare, expected_error.clone());
    validate_tx_expect_error(&mut mempool, &ValidationArgs::from(&declare), expected_error);
}
```
