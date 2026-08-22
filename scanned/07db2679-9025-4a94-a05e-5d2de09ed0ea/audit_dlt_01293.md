# [?] Prevent Overflow LRU Cache from Exploding (#4801)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2023-10-11
Source: https://github.com/sigp/lighthouse/commit/8660043024f95a31db9b0027a2e9eacc28d7e727
Type: security-commit

## Details
Prevent Overflow LRU Cache from Exploding (#4801)

* Initial Commit of State LRU Cache

* Build State Caches After Reconstruction

* Cleanup Duplicated Code in OverflowLRUCache Tests

* Added Test for State LRU Cache

* Prune Cache of Old States During Maintenance

* Address Michael's Comments

* Few More Comments

* Removed Unused impl

* Last touch up

* Fix Clippy
