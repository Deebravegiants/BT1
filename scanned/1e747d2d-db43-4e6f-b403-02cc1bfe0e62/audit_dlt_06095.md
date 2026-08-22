# [?] Fix Array Deserialization Panic (#837)

## Summary
Severity: Unknown
Chain: ZK
Component: arkworks-rs/algebra
Published: 2024-06-19
Source: https://github.com/arkworks-rs/algebra/commit/79a5fe3f0e17ecec7aa683fa58dd02e14eb28a8b
Type: security-commit

## Details
Fix Array Deserialization Panic (#837)

* Fix Array Deserialization Panic

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Amend CHANGELOG

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Use ArrayVec instead of unsafe

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Unrelated fmt

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Defensive programming not needed

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* .ok().unwrap()

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

---------

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>
Co-authored-by: Pratyush Mishra <pratyushmishra@berkeley.edu>
