# [?] fix(runtime): Avoid panicking if `stake_rewards` capacity turns out be larger (#13697)

## Summary
Severity: Unknown
Chain: Solana
Component: jito-foundation/jito-solana
Published: 2026-07-08
Source: https://github.com/jito-foundation/jito-solana/commit/9310132e7ff0195e33e09b5fc32f6db4d0a42b1b
Type: security-commit

## Details
fix(runtime): Avoid panicking if `stake_rewards` capacity turns out be larger (#13697)

* fix(runtime): Avoid panicking if `stake_rewards` capacity turns out be larger

Using `zip_eq` is dangerous, it panics when the iterators yield
different amount of elements. Such scenario is not unlikely in this
code, since `with_capacity()` might allocate more memory than requested.

Use `zip` to make sure such panic never happens. `zip` stops yielding
once one of the iterators stops yielding, so it will not yield over the
length of `stake_delegations`.

The issue (fortunately) didn't occur on any validator, and never
appeared in tests. Nevertheless, this change was tested by replaying an
epoch boundary with:

```
$ agave-ledger-tool verify --force-update-to-open --halt-at-slot 412128000
```

And succeeded without any issues.

* fix(runtime): Add more safeguards

* Explicitly slice the `stake_rewards.spare_capacity_mut()` to
  `stake_delegations.len()`.
* Debug assert that `num_stake_rewards` is lower or equal to
  `stake_delegations_len`.

## Patch
### runtime/src/bank/partitioned_epoch_rewards/calculation.rs
```diff
@@ -718,11 +718,12 @@ impl Bank {
         // Producing the stake reward with rayon triggers a lot of
         // (re)allocations. To avoid that, we allocate it at the start and
         // pass `stake_rewards.spare_capacity_mut()` as one of iterators.
-        let mut stake_rewards = PartitionedStakeRewards::with_capacity(stake_delegations.len());
+        let stake_delegations_len = stake_delegations.len();
+        let mut stake_rewards = PartitionedStakeRewards::with_capacity(stake_delegations_len);
         let rewards_accumulator: RewardsAccumulator = thread_pool.install(|| {
             stake_delegations
                 .par_iter()
-                .zip_eq(stake_rewards.spare_capacity_mut())
+                .zip(&mut stake_rewards.spare_capacity_mut()[..stake_delegations_len])
                 .with_min_len(500)
                 .filter_map(|((stake_pubkey, stake_account), stake_reward_ref)| {
                     let maybe_reward_record = self.redeem_delegation_rewards(
@@ -793,7 +794,9 @@ impl Bank {
             num_stake_rewards,
             total_stake_rewards_lamports,
         } = rewards_accumulator;
-        // SAFETY: We initialized all the `stake_rewards` elements up to the capacity.
+        // SAFETY: We initialized all the `stake_rewards` elements up to
+        // `num_stake_rewards`.
+        debug_assert!(num_stake_rewards <= stake_delegations_len);
         unsafe {
             stake_rewards.assume_init(num_stake_rewards);
         }
```
