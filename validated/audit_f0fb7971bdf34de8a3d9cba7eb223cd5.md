### Title
Deprecated `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim` excludes proof size of preceding transaction extensions from `BlockWeight` reclaim/charge, causing systematic PoV accounting drift - (File: cumulus/primitives/storage-weight-reclaim/src/lib.rs)

### Summary
The deprecated `StorageWeightReclaim` extension only measures proof-size consumption between its own `prepare` and `post_dispatch_details` hooks, so any storage proof size consumed by transaction extensions that execute *before* it in the pipeline (e.g. `ChargeTransactionPayment` storage reads) is never counted into `consumed_weight`, while `benchmarked_weight` is derived from the dispatched call's own weight info. This mismatch is explicitly acknowledged as a defect in `prdoc/stable2503/pr_6140.prdoc`, and the extension itself carries a `#[deprecated]` attribute stating it "ignores the validation and preparation of extensions prior to itself." The deprecated type is still compiled into and referenced by `cumulus/parachains/runtimes/contracts/contracts-rococo/src/lib.rs`, confirming it remains reachable in a real parachain runtime rather than being purely a dead legacy path.

### Finding Description
`StorageWeightReclaim::post_dispatch_details` (`cumulus/primitives/storage-weight-reclaim/src/lib.rs:163-226`) computes:
- `benchmarked_weight` from `info.total_weight().proof_size()` minus `unspent` (`line 184-185`), which reflects only the dispatched call's declared/benchmarked weight, not any extensions ahead of it in the pipeline;
- `consumed_weight` as the delta of the node-reported proof size between this extension's own `prepare` (`line 152-161`) and `post_dispatch_details` calls (`line 186`).

If `StorageWeightReclaim` is not the outermost wrapper of the full extension tuple (which the deprecated struct architecturally cannot be, since unlike `cumulus_pallet_weight_reclaim::StorageWeightReclaim` it does not take a wrapped-extension type parameter), any proof-size-consuming work done by extensions ordered before it (typically `ChargeTransactionPayment`, which reads account/asset storage to determine fees) is invisible to `consumed_weight`. The subsequent `frame_system::BlockWeight::<T>::mutate` block (`lines 195-224`) then either `accrue`s or `reduce`s `frame_system::BlockWeight` based on `storage_size_diff = benchmarked_weight.abs_diff(consumed_weight)`, propagating the skew into the canonical on-chain PoV accounting for every extrinsic processed through that pipeline.

This is the exact defect documented in `prdoc/stable2503/pr_6140.prdoc` lines 10-12 and 35 ("prior to transaction extension, StorageWeightReclaim also missed the some proof size used by other transaction extension prior to itself. This is also fixed by the wrapping StorageWeightReclaim"), and is why the type carries the deprecation note at `cumulus/primitives/storage-weight-reclaim/src/lib.rs:114-118`.

The precondition — a runtime that still uses the deprecated non-wrapping extension — is not hypothetical: `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim` is referenced in `cumulus/parachains/runtimes/contracts/contracts-rococo/src/lib.rs`, so the mis-accounting path is reachable in-tree, not merely a theoretical config choice.

Any signed user submitting ordinary extrinsics against such a runtime triggers this path — no privileged origin, proxy bypass, or special call is required. The extension has no check that rejects itself when not wrapping the whole pipeline; it silently mis-measures, and `CheckWeight`/`BlockWeight` bookkeeping downstream trusts its output unconditionally.

### Impact Explanation
Because `frame_system::BlockWeight` under- or over-corrects proof-size accounting on every extrinsic routed through the misordered/non-wrapping pipeline, an attacker submitting extrinsics that trigger storage-heavy pre-`StorageWeightReclaim` extension logic (fee payment storage reads) can cause the recorded PoV weight to diverge from the true node-side proof size. Over many extrinsics this drift accumulates in `BlockWeight`, which can let the chain systematically underprice PoV usage (reclaiming too much, allowing more real proof-size consumption than the runtime believes it has spent) or, conversely, overprice it (wasting block capacity). This is a persistent accounting-integrity defect in a component whose entire purpose is precise PoV cost bookkeeping.

### Likelihood Explanation
The precondition (deprecated extension not wrapping the full pipeline) is a runtime-configuration choice, but it is not theoretical: `contracts-rococo-runtime` in this monorepo still imports and uses the deprecated `StorageWeightReclaim` type. Every normal signed extrinsic on that chain exercises the flawed accounting path, making the issue continuously and trivially reproducible without any special attacker capability — it is triggered by ordinary transaction submission.

### Recommendation
Migrate all remaining runtimes (including `contracts-rococo-runtime`) off `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim` onto `cumulus_pallet_weight_reclaim::StorageWeightReclaim`, wrapping the entire transaction extension pipeline as shown in `prdoc/stable2503/pr_6140.prdoc`. Consider adding a runtime-construction-time or `try-runtime` lint that fails if the deprecated extension type is present in a production `TxExtension` tuple, to prevent silent reintroduction.

### Proof of Concept
Differential integration test (in `cumulus/primitives/storage-weight-reclaim/src/tests.rs` style, or a dedicated `contracts-rococo` runtime test):
1. Construct two mock transaction-extension pipelines with identical dispatchables and identical `ChargeTransactionPayment`-like storage-reading extension: (a) `(ChargeTransactionPayment, cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim, CheckWeight)` and (b) `cumulus_pallet_weight_reclaim::StorageWeightReclaim<(ChargeTransactionPayment, CheckWeight)>`.
2. Dispatch the same extrinsic through both, using the `PROOF_RECORDING_DISABLED`-independent host-function proof size mock to simulate storage reads in `ChargeTransactionPayment`.
3. Assert `frame_system::BlockWeight::<T>::get().proof_size()` after dispatch is identical for both cases.
4. Expect the assertion to fail for pipeline (a): the pre-`StorageWeightReclaim` storage reads from `ChargeTransactionPayment` are excluded from `consumed_weight`, producing a different `storage_size_diff` and thus a different final `BlockWeight` than pipeline (b), confirming the accounting divergence.