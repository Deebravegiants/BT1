No vulnerability found for this question.

**Analysis:**

The premise doesn't hold up against the actual code. When `randomness::on_new_block` is invoked with `seed_for_new_block = None` (as happens in the non-DKG `block_prologue` at [1](#0-0) ), `PerBlockRandomness.seed` is set to `option::none()`.

Any subsequent call to `next_32_bytes` — which is the function `object::create_object`'s `#[randomness]`-gated codepaths would ultimately reach — does two things in order: first it asserts `is_unbiasable()` (a native check on transaction shape/annotation), then it does `*randomness.seed.borrow()` at [2](#0-1) . Move's `Option::borrow` aborts when the option is empty. So if `seed` is `None`, this line **aborts the transaction** rather than silently proceeding with a predictable/zero seed. This is exactly what the question's own proof-of-concept idea predicts as the expected (safe) behavior — and it is what the code actually does, confirmed by the spec's `NextBlobAbortsIf` schema which explicitly states `aborts_if option::is_none(randomness.seed)` at [3](#0-2) .

There is no code path where a `None` seed leads to silent use of a predictable value — it leads to an abort, preserving the unbiasability invariant.

Separately, the review bounds require the path to originate from unprivileged transaction/API/bytecode input. `BlockMetadataExt` is a system-generated block-prologue transaction constructed by consensus/validators (e.g. via `new_metadata_with_randomness` at [4](#0-3) ) and executed as the VM signer (`system_addresses::assert_vm(vm)` at [5](#0-4) ). An unprivileged user/transaction cannot forge or replay this into the prologue — that would require compromising consensus itself, which is explicitly out of scope ("Ignore malicious peer or node behavior").

Given both (a) the abort-on-`None` behavior already enforces the unbiasability invariant, and (b) the entry point is not reachable from unprivileged input, this does not meet the custody-impact gate.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/block.move (L213-226)
```text
    ) acquires BlockResource, CommitHistory {
        let epoch_interval =
            block_prologue_common(
                &vm,
                hash,
                epoch,
                round,
                proposer,
                failed_proposer_indices,
                previous_block_votes_bitvec,
                timestamp
            );
        randomness::on_new_block(&vm, epoch, round, option::none());
        decryption::on_new_block(&vm, epoch, round, option::none());
```

**File:** aptos-move/framework/aptos-framework/sources/randomness.move (L62-68)
```text
    public(friend) fun on_new_block(
        vm: &signer,
        epoch: u64,
        round: u64,
        seed_for_new_block: Option<vector<u8>>
    ) acquires PerBlockRandomness {
        system_addresses::assert_vm(vm);
```

**File:** aptos-move/framework/aptos-framework/sources/randomness.move (L79-90)
```text
    fun next_32_bytes(): vector<u8> acquires PerBlockRandomness {
        assert!(is_unbiasable(), E_API_USE_IS_BIASIBLE);

        let input = DST;
        let randomness = borrow_global<PerBlockRandomness>(@aptos_framework);
        let seed = *randomness.seed.borrow();

        input.append(seed);
        input.append(transaction_context::get_transaction_hash());
        input.append(fetch_and_increment_txn_counter());
        hash::sha3_256(input)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/randomness.spec.move (L71-76)
```text
    spec schema NextBlobAbortsIf {
        let randomness = global<PerBlockRandomness>(@aptos_framework);
        aborts_if option::is_none(randomness.seed);
        aborts_if !spec_is_unbiasable();
        aborts_if !exists<PerBlockRandomness>(@aptos_framework);
    }
```

**File:** consensus/consensus-types/src/block.rs (L572-592)
```rust
    pub fn new_metadata_with_randomness(
        &self,
        validators: &[AccountAddress],
        randomness: Option<Randomness>,
    ) -> BlockMetadataExt {
        BlockMetadataExt::new_v1(
            self.id(),
            self.epoch(),
            self.round(),
            self.author().unwrap_or(AccountAddress::ZERO),
            self.previous_bitvec().into(),
            // For nil block, we use 0x0 which is convention for nil address in move.
            self.block_data()
                .failed_authors()
                .map_or(vec![], |failed_authors| {
                    Self::failed_authors_to_indices(validators, failed_authors)
                }),
            self.timestamp_usecs(),
            randomness,
        )
    }
```
