# [?] Fix reentrancy of FrozenBalance::died hook (#10473)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2022-02-11
Source: https://github.com/paritytech/substrate/commit/a9020646e784170050a4e6324dd067ab0e5af448
Type: security-commit

## Details
Fix reentrancy of FrozenBalance::died hook (#10473)

* assets: execute `died` hook outside of mutate

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>

* assets: extend tests for `died` hook

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>

* assets: update doc of FrozenBalance::died

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>

* assets: review fixes

- fix cases where `died` should not have been called
- use `Option<DeadConsequence>` instead of `DeadConsequence`

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>

* assets: update comment in mock.rs

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>

* assets: return `Remove` in dead_account

The return value is ignored in the only case that it is produced
by a call, but having it this way makes it more understandable.

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>
