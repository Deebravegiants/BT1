# [?] fix(db): Fix a sprout/history tree read panic in Zebra 1.4.0, which only happens before the 25.3.0 state upgrade completes (#7972)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2023-11-22
Source: https://github.com/ZcashFoundation/zebra/commit/d20ec3940e2fabae75189976cfd9aafe279e34f0
Type: security-commit

## Details
fix(db): Fix a sprout/history tree read panic in Zebra 1.4.0, which only happens before the 25.3.0 state upgrade completes (#7972)

* Avoid a race condition in the 25.3.0 state upgrade

* Look for the most recent sprout tree height if needed

* Get the latest history tree not the tip height history tree

* Discard keys provided by low level database method

* Remove extra ;

* Provide key types & rustfmt

* Fix weird closure type syntax

* Update zebra-state/src/service/finalized_state/disk_format/upgrade/fix_tree_key_type.rs

Co-authored-by: Marek <mail@marek.onl>

---------

Co-authored-by: Marek <mail@marek.onl>
