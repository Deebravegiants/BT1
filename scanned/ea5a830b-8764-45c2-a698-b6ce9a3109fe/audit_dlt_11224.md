# [?] fix(acvm): reject out-of-range Keccakf1600 lanes instead of panicking (#13319)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-07-13
Source: https://github.com/noir-lang/noir/commit/e5639b2fe0d387aa2a66f55b09597d3bd45acea3
Type: security-commit

## Details
fix(acvm): reject out-of-range Keccakf1600 lanes instead of panicking (#13319)

## Patch
### acvm-repo/acvm/src/compiler/validator.rs
```diff
@@ -299,8 +299,15 @@ pub fn validate_witness<F: AcirField>(
                         let mut state = [0; 25];
                         for (it, input) in state.iter_mut().zip_eq(inputs.as_ref()) {
                             let witness_assignment = input_to_value(witness_map, *input)?;
-                            let lane = witness_assignment.try_to_u64();
-                            *it = lane.unwrap();
+                            check_fits_in_bits(
+                                witness_assignment,
+                                64,
+                                opcode_index,
+                                "Keccakf1600",
+                            )?;
+                            *it = witness_assignment
+                                .try_to_u64()
+                                .expect("value was just checked to fit in 64 bits");
                         }
                         let output_state = keccakf1600(state)?;
                         for (output_witness, value) in outputs.iter().zip_eq(output_state) {
@@ -510,6 +517,38 @@ mod tests {
         }
     }
 
+    /// Builds a Keccakf1600 circuit over input witnesses `0..25` and output witnesses `25..50`.
+    fn keccakf1600_circuit() -> Circuit<FieldElement> {
+        let inputs: Box<[FunctionInput<FieldElement>; 25]> =
+            Box::new(std::array::from_fn(|i| FunctionInput::Witness(Witness(i as u32))));
+        let outputs: Box<[Witness; 25]> =
+            Box::new(std::array::from_fn(|i| Witness((25 + i) as u32)));
+        make_circuit(vec![Opcode::BlackBoxFuncCall(BlackBoxFuncCall::Keccakf1600 {
+            inputs,
+            outputs,
+        })])
+    }
+
+    #[test]
+    fn test_keccakf1600_out_of_range_lane_does_not_panic() {
+        // A lane holding 2^64 does not fit in 64 bits: `validate_witness` must report a
+        // graceful, opcode-located constraint violation rather than panicking on the
+        // internal `try_to_u64` conversion.
+        let circuit = keccakf1600_circuit();
+        let mut witness_map = WitnessMap::new();
+        witness_map.insert(Witness(0), FieldElement::from(1u128 << 64));
+        for i in 1..50u32 {
+            witness_map.insert(Witness(i), FieldElement::zero());
+        }
+
+        let backend = Bn254BlackBoxSolver;
+        assert_unsatisfied_constraint(
+            validate_witness(&backend, &witness_map, &circuit),
+            0,
+            "Keccakf1600 opcode violation: value 18446744073709551616 does not fit in 64 bits",
+        );
+    }
+
     #[test]
     fn test_assert_zero_valid() {
         // w1 + w2 - w3 = 0, where w1=2, w2=3, w3=5
```

### acvm-repo/acvm/src/pwg/blackbox/mod.rs
```diff
@@ -9,7 +9,10 @@ use itertools::Itertools;
 use self::{aes128::solve_aes128_encryption_opcode, hash::solve_poseidon2_permutation_opcode};
 
 use super::{OpcodeNotSolvable, OpcodeResolutionError, insert_value};
-use crate::{BlackBoxFunctionSolver, pwg::input_to_value};
+use crate::{
+    BlackBoxFunctionSolver,
+    pwg::{check_bit_size, input_to_value},
+};
 
 pub(crate) mod aes128;
 pub(crate) mod embedded_curve_ops;
@@ -102,8 +105,10 @@ pub(crate) fn solve<F: AcirField>(
             let mut state = [0; 25];
             for (it, input) in state.iter_mut().zip_eq(inputs.as_ref()) {
                 let witness_assignment = input_to_value(initial_witness, *input)?;
-                let lane = witness_assignment.try_to_u64();
-                *it = lane.unwrap();
+                check_bit_size(witness_assignment, 64)?;
+                *it = witness_assignment
+                    .try_to_u64()
+                    .expect("value was just checked to fit in 64 bits");
             }
             let output_state = keccakf1600(state)?;
             for (output_witness, value) in outputs.iter().zip_eq(output_state) {
```

### acvm-repo/acvm/tests/solver.rs
```diff
@@ -15,7 +15,7 @@ use acir::{
 use acir::{InvalidInputBitSize, parse_opcodes};
 
 use acvm::pwg::{ACVM, ACVMStatus, ErrorLocation, ForeignCallWaitInfo, OpcodeResolutionError};
-use acvm_blackbox_solver::StubbedBlackBoxSolver;
+use acvm_blackbox_solver::{StubbedBlackBoxSolver, keccakf1600};
 use bn254_blackbox_solver::Bn254BlackBoxSolver;
 use brillig_vm::brillig::HeapValueType;
 
@@ -1121,6 +1121,60 @@ fn keccakf1600_zeros() {
     assert_eq!(results, Ok(expected_results));
 }
 
+/// Runs a single Keccakf1600 opcode over the given 25 input lanes (as witnesses) and
+/// returns the ACVM status plus the finalized witness map so tests can inspect outputs.
+fn run_keccakf1600(
+    input_lanes: [FieldElement; 25],
+) -> (ACVMStatus<FieldElement>, WitnessMap<FieldElement>) {
+    let solver = Bn254BlackBoxSolver;
+
+    let inputs: Box<[FunctionInput<FieldElement>; 25]> =
+        Box::new(std::array::from_fn(|i| FunctionInput::Witness(Witness(i as u32))));
+    let outputs: Box<[Witness; 25]> = Box::new(std::array::from_fn(|i| Witness((25 + i) as u32)));
+
+    let mut witness = BTreeMap::new();
+    for (i, lane) in input_lanes.iter().enumerate() {
+        witness.insert(Witness(i as u32), *lane);
+    }
+    let initial_witness = WitnessMap::from(witness);
+
+    let opcodes = [Opcode::BlackBoxFuncCall(BlackBoxFuncCall::Keccakf1600 { inputs, outputs })];
+    let mut acvm = ACVM::new(&solver, &opcodes, initial_witness, &[], &[]);
+    let status = acvm.solve();
+    // `finalize` panics unless the ACVM solved; only harvest outputs in that case.
+    let witness_map =
+        if status == ACVMStatus::Solved { acvm.finalize() } else { WitnessMap::new() };
+    (status, witness_map)
+}
+
+#[test]
+fn keccakf1600_accepts_max_u64_lane_and_computes_real_output() {
+    // Boundary: `u64::MAX` is the largest valid lane, so the range gate must let it through
+    // and produce exactly the reference `keccakf1600` output.
+    let mut input_state = [0u64; 25];
+    input_state[0] = u64::MAX;
+    let input_lanes = input_state.map(|lane| FieldElement::from(u128::from(lane)));
+
+    let (status, witness_map) = run_keccakf1600(input_lanes);
+    assert_eq!(status, ACVMStatus::Solved);
+
+    let expected = keccakf1600(input_state).unwrap();
+    for (i, expected_lane) in expected.iter().enumerate() {
+        let got = witness_map.get(&Witness((25 + i) as u32)).expect("output lane set");
+        assert_eq!(*got, FieldElement::from(u128::from(*expected_lane)), "lane {i} mismatch");
+    }
+}
+
+#[test]
+fn keccakf1600_rejects_out_of_range_lane() {
+    // A lane holding 2^64 does not fit in 64 bits: the solver must fail gracefully rather
+    // than panicking on the internal `try_to_u64` conversion.
+    let mut input_lanes = [FieldElement::zero(); 25];
+    input_lanes[0] = FieldElement::from(1u128 << 64);
+    let (status, _) = run_keccakf1600(input_lanes);
+    assert!(matches!(status, ACVMStatus::Failure(_)), "expected graceful failure, got {status:?}");
+}
+
 // NOTE: an "average" bigint is large, so consider increasing the number of proptest shrinking
 // iterations (from the default 1024) to reach a simplified case, e.g.
 // PROPTEST_MAX_SHRINK_ITERS=1024000
```
