# [?] fix: add a constraint for SSTORE gas reentrancy sentry (#1225)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/zkevm-circuits
Published: 2023-02-21
Source: https://github.com/privacy-ethereum/zkevm-circuits/commit/8d6bd6aa8610ed842a3b76d51279998c2e13d729
Type: security-commit

## Details
fix: add a constraint for SSTORE gas reentrancy sentry (#1225)

### Description

Constrain SSTORE with gas reentrancy sentry. Gas reentrancy sentry could
be referenced in [this go-ethereum
code](https://github.com/ethereum/go-ethereum/blob/master/core/vm/operations_acl.go#L30).

### Issue Link

Close
https://github.com/privacy-scaling-explorations/zkevm-circuits/issues/1214

### Type of change

- [X] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing
functionality to not work as expected)
- [ ] This change requires a documentation update

### Contents

- [_item_]

### Rationale

[_design decisions and extended information_]

### How Has This Been Tested?

Could be tested with previous SSTORE gadget test cases.

<hr>

## How to fill a PR description 

Please give a concise description of your PR.

The target readers could be future developers, reviewers, and auditors.
By reading your description, they should easily understand the changes
proposed in this pull request.

MUST: Reference the issue to resolve

### Single responsability

Is RECOMMENDED to create single responsibility commits, but not
mandatory.

Anyway, you MUST enumerate the changes in a unitary way, e.g.

```
This PR contains:
- Cleanup of xxxx, yyyy
- Changed xxxx to yyyy in order to bla bla
- Added xxxx function to ...
- Refactored ....
```

### Design choices

RECOMMENDED to:
- What types of design choices did you face?
- What decisions you have made?
- Any valuable information that could help reviewers to think critically

## Patch
### zkevm-circuits/src/evm_circuit/execution/sstore.rs
```diff
@@ -1,13 +1,14 @@
 use crate::{
     evm_circuit::{
         execution::ExecutionGadget,
+        param::N_BYTES_GAS,
         step::ExecutionState,
         util::{
             common_gadget::{SameContextGadget, SstoreGasGadget},
             constraint_builder::{
                 ConstraintBuilder, ReversionInfo, StepStateTransition, Transition::Delta,
             },
-            math_gadget::{IsEqualGadget, IsZeroGadget},
+            math_gadget::{IsEqualGadget, IsZeroGadget, LtGadget},
             not, CachedRegion, Cell,
         },
         witness::{Block, Call, ExecStep, Transaction},
@@ -35,6 +36,8 @@ pub(crate) struct SstoreGadget<F> {
     phase2_original_value: Cell<F>,
     is_warm: Cell<F>,
     tx_refund_prev: Cell<F>,
+    // Constrain for SSTORE reentrancy sentry.
+    sufficient_gas_sentry: LtGadget<F, N_BYTES_GAS>,
     gas_cost: SstoreGasGadget<F>,
     tx_refund: SstoreTxRefundGadget<F>,
 }
@@ -86,6 +89,18 @@ impl<F: Field> ExecutionGadget<F> for SstoreGadget<F> {
             Some(&mut reversion_info),
         );
 
+        // Constrain for SSTORE reentrancy sentry.
+        let sufficient_gas_sentry = LtGadget::construct(
+            cb,
+            GasCost::SSTORE_SENTRY.0.expr(),
+            cb.curr.state.gas_left.expr(),
+        );
+        cb.require_equal(
+            "Gas left must be greater than gas sentry",
+            sufficient_gas_sentry.expr(),
+            1.expr(),
+        );
+
         let gas_cost = SstoreGasGadget::construct(
             cb,
             phase2_value.clone(),
@@ -131,6 +146,7 @@ impl<F: Field> ExecutionGadget<F> for SstoreGadget<F> {
             phase2_original_value,
             is_warm,
             tx_refund_prev,
+            sufficient_gas_sentry,
             gas_cost,
             tx_refund,
         }
@@ -188,6 +204,13 @@ impl<F: Field> ExecutionGadget<F> for SstoreGadget<F> {
         self.tx_refund_prev
             .assign(region, offset, Value::known(F::from(tx_refund_prev)))?;
 
+        self.sufficient_gas_sentry.assign_value(
+            region,
+            offset,
+            Value::known(F::from(GasCost::SSTORE_SENTRY.0)),
+            Value::known(F::from(step.gas_left)),
+        )?;
+
         self.gas_cost
             .assign(region, offset, value, value_prev, original_value, is_warm)?;
 
```
