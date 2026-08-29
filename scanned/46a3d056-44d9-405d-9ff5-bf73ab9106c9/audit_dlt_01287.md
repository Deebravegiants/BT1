# [?] Fix data columns not persisting for PeerDAS due to a `getBlobs` race condition (#6756)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-01-15
Source: https://github.com/sigp/lighthouse/commit/dd7591f7123dfe072631c0deb0abc1b78cc82733
Type: security-commit

## Details
Fix data columns not persisting for PeerDAS due to a `getBlobs` race condition (#6756)

* Fix data columns not persisting for PeerDAS due to a `getBlobs` race condition.

* Refactor blobs and columns logic in `chain.import_block` for clarity. Add more docs on `data_column_recv`.

* Add more code comments for clarity.

* Merge remote-tracking branch 'origin/unstable' into fix-column-race

# Conflicts:
#	beacon_node/beacon_chain/src/block_verification_types.rs
#	beacon_node/beacon_chain/src/data_availability_checker/overflow_lru_cache.rs

* Fix lint.
