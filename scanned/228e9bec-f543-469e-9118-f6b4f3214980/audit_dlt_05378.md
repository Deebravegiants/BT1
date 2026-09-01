# [?] Fix/issue 769 overflow protection (#780)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2025-12-30
Source: https://github.com/kaspanet/rusty-kaspa/commit/cea06453b0172ed7c02d19962836b5ebeb1dddec
Type: security-commit

## Details
Fix/issue 769 overflow protection (#780)

* fix: prevent integer overflow in estimate_block_count() (issue #769)

- Replace subtraction with saturating_sub() to prevent panic when
  virtual_score < retention_period_root_score during IBD UTXO import
- Add test to verify overflow protection works correctly
- Fixes: https://github.com/kaspanet/rusty-kaspa/issues/769

* Coder and freshair req

* test removed

* Removed

   daa_score: pruning_point_header.daa_score,
            bits: pruning_point_header.bits,
            past_median_time: pruning_point_header.timestamp,
            mergeset_non_daa: BlockHashSet::from_iter(std::iter::once(pruning_point)),
