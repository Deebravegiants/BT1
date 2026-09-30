# [?] Merge remote-tracking branch 'ckb-ghsa-fjj4-2q73-jvgc/zhangsoledad/fix-resume-cycles' into rc/v0.103

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2022-04-11
Source: https://github.com/nervosnetwork/ckb/commit/dedb16c37aeb56908e3adacd5b8afc900d9a15d0
Type: security-commit

## Details
Merge remote-tracking branch 'ckb-ghsa-fjj4-2q73-jvgc/zhangsoledad/fix-resume-cycles' into rc/v0.103

## Patch
### Cargo.lock
```diff
@@ -1132,6 +1132,7 @@ dependencies = [
  "faster-hex",
  "goblin 0.2.3",
  "proptest",
+ "rand 0.8.5",
  "serde",
  "tempfile",
  "tiny-keccak",
```

### script/Cargo.toml
```diff
@@ -39,3 +39,4 @@ tiny-keccak = { version = "2.0", features = ["sha3"] }
 ckb-crypto = { path = "../util/crypto", version = "= 0.102.0" }
 ckb-db-schema = { path = "../db-schema", version = "= 0.102.0" }
 tempfile = "3.0"
+rand = "0.8.4"
```

### script/src/types.rs
```diff
@@ -8,7 +8,8 @@ use ckb_vm::{
     machine::{VERSION0, VERSION1},
     memory::{FLAG_EXECUTABLE, FLAG_FREEZED},
     snapshot::{make_snapshot, Snapshot},
-    CoreMachine as _, Memory, SupportMachine, ISA_B, ISA_IMC, ISA_MOP, RISCV_PAGESIZE,
+    CoreMachine as _, Error as VMInternalError, Memory, SupportMachine, ISA_B, ISA_IMC, ISA_MOP,
+    RISCV_PAGESIZE,
 };
 use serde::{Deserialize, Serialize};
 use std::fmt;
@@ -100,33 +101,48 @@ pub(crate) type Machine<'a> = AsmMachine<'a>;
 pub(crate) type Machine<'a> = TraceMachine<'a, CoreMachine>;
 
 pub struct ResumableMachine<'a> {
-    pub(crate) machine: Machine<'a>,
-    pub(crate) program_loaded: bool,
+    machine: Machine<'a>,
+    pub(crate) program_bytes_cycles: Option<Cycle>,
+    pub(crate) enable_2021: bool,
 }
 
 impl<'a> ResumableMachine<'a> {
-    pub(crate) fn new(machine: Machine<'a>, program_loaded: bool) -> Self {
+    pub(crate) fn new(
+        machine: Machine<'a>,
+        program_bytes_cycles: Option<Cycle>,
+        enable_2021: bool,
+    ) -> Self {
         ResumableMachine {
             machine,
-            program_loaded,
+            program_bytes_cycles,
+            enable_2021,
         }
     }
 
     pub(crate) fn cycles(&self) -> Cycle {
         self.machine.machine.cycles()
     }
 
-    #[cfg(test)]
-    pub(crate) fn set_cycles(&mut self, cycles: Cycle) {
-        self.machine.machine.set_cycles(cycles)
-    }
-
     pub(crate) fn set_max_cycles(&mut self, cycles: Cycle) {
         set_vm_max_cycles(&mut self.machine, cycles)
     }
 
     pub fn program_loaded(&self) -> bool {
-        self.program_loaded
+        self.program_bytes_cycles.is_none()
+    }
+
+    pub fn add_cycles(&mut self, cycles: Cycle) -> Result<(), VMInternalError> {
+        self.machine.machine.add_cycles(cycles)
+    }
+
+    pub fn run(&mut self) -> Result<i8, VMInternalError> {
+        if let Some(cycles) = self.program_bytes_cycles {
+            if self.enable_2021 {
+                self.add_cycles(cycles)?;
+                self.program_bytes_cycles = None;
+            }
+        }
+        self.machine.run()
     }
 }
 
@@ -275,7 +291,7 @@ impl TryFrom<TransactionState<'_>> for TransactionSnapshot {
 
         let (snap, current_cycles) = if let Some(mut vm) = vm {
             // we should not capture snapshot if load program failed by exceeded cycles
-            if vm.program_loaded {
+            if vm.program_loaded() {
                 let vm_cycles = vm.cycles();
                 // To be consistent with the mainnet, add this flag to enable this behavior after hardfork
                 if !enable_backup_page_flags {
```

### script/src/verify.rs
```diff
@@ -669,7 +669,7 @@ impl<'a, DL: CellDataProvider + HeaderProvider> TransactionScriptsVerifier<'a, D
 
         if let Some(mut vm) = vm {
             vm.set_max_cycles(limit_cycles);
-            match vm.machine.run() {
+            match vm.run() {
                 Ok(code) => {
                     self.tracing_data_as_code_pages.borrow_mut().clear();
                     if code == 0 {
@@ -1017,9 +1017,14 @@ impl<'a, DL: CellDataProvider + HeaderProvider> TransactionScriptsVerifier<'a, D
             let bytes = machine
                 .load_program(&program, &[])
                 .map_err(map_vm_internal_error)?;
-            let load_ret = machine.machine.add_cycles(transferred_byte_cycles(bytes));
+            let program_bytes_cycles = transferred_byte_cycles(bytes);
+            let load_ret = machine.machine.add_cycles(program_bytes_cycles);
             if matches!(load_ret, Err(ref error) if error == &VMInternalError::CyclesExceeded) {
-                return Ok(ChunkState::suspended(ResumableMachine::new(machine, false)));
+                return Ok(ChunkState::suspended(ResumableMachine::new(
+                    machine,
+                    Some(program_bytes_cycles),
+                    self.is_vm_version_1_and_syscalls_2_enabled(),
+                )));
             }
             load_ret.map_err(|e| ScriptError::VMInternalError(format!("{:?}", e)))?;
         }
@@ -1035,7 +1040,11 @@ impl<'a, DL: CellDataProvider + HeaderProvider> TransactionScriptsVerifier<'a, D
             }
             Err(error) => match error {
                 VMInternalError::CyclesExceeded => {
-                    Ok(ChunkState::suspended(ResumableMachine::new(machine, true)))
+                    Ok(ChunkState::suspended(ResumableMachine::new(
+                        machine,
+                        None,
+                        self.is_vm_version_1_and_syscalls_2_enabled(),
+                    )))
                 }
                 _ => {
                     self.tracing_data_as_code_pages.borrow_mut().clear();
```

### script/src/verify/tests/ckb_latest/features_since_v2019.rs
```diff
@@ -1252,3 +1252,64 @@ fn check_debugger() {
     let result = verifier.verify_without_limit(script_version, &rtx);
     assert!(result.is_ok(), "result {:?}", result);
 }
+
+#[test]
+fn check_typical_secp256k1_blake160_2_in_2_out_resume_load_cycles() {
+    _check_typical_secp256k1_blake160_2_in_2_out_resume_load_cycles(23);
+    _check_typical_secp256k1_blake160_2_in_2_out_resume_load_cycles(34);
+    _check_typical_secp256k1_blake160_2_in_2_out_resume_load_cycles(44);
+}
+
+fn _check_typical_secp256k1_blake160_2_in_2_out_resume_load_cycles(step_cycles: Cycle) {
+    const LOAD_CYCLES: Cycle = 25356;
+
+    let script_version = SCRIPT_VERSION;
+    let rtx = random_2_in_2_out_rtx();
+    let mut cycles = 0;
+    let verifier = TransactionScriptsVerifierWithEnv::new();
+
+    let result = verifier.verify_map(script_version, &rtx, |verifier| {
+        let mut init_state: Option<TransactionState<'_>> = None;
+
+        if let VerifyResult::Suspended(state) = verifier.resumable_verify(step_cycles).unwrap() {
+            init_state = Some(state);
+        }
+
+        loop {
+            let state = init_state.take().unwrap();
+            let (limit_cycles, _last) = state.next_limit_cycles(step_cycles, TWO_IN_TWO_OUT_CYCLES);
+            match verifier.resume_from_state(state, limit_cycles).unwrap() {
+                VerifyResult::Suspended(state) => init_state = Some(state),
+                VerifyResult::Completed(cycle) => {
+                    cycles = cycle;
+                    break;
+                }
+            }
+        }
+
+        verifier.verify(TWO_IN_TWO_OUT_CYCLES)
+    });
+
+    let cycles_once = result.unwrap();
+    assert!(
+        cycles <= TWO_IN_TWO_OUT_CYCLES,
+        "step_cycles {}",
+        step_cycles
+    );
+    assert!(
+        cycles >= TWO_IN_TWO_OUT_CYCLES - CYCLE_BOUND,
+        "step_cycles {}",
+        step_cycles
+    );
+
+    if SCRIPT_VERSION >= ScriptVersion::V1 {
+        assert_eq!(cycles, cycles_once, "step_cycles {}", step_cycles);
+    } else {
+        assert_eq!(
+            cycles + LOAD_CYCLES,
+            cycles_once,
+            "step_cycles {}",
+            step_cycles
+        );
+    }
+}
```

### script/src/verify/tests/ckb_latest/features_since_v2021.rs
```diff
@@ -7,6 +7,10 @@ use ckb_types::{
     packed::{self, CellDep, CellInput, CellOutputBuilder, OutPoint, Script},
 };
 use ckb_vm::Error as VmError;
+use proptest::{prelude::*, prop_assert_eq, proptest};
+use rand::distributions::Uniform;
+use rand::{thread_rng, Rng};
+use std::collections::VecDeque;
 
 use super::SCRIPT_VERSION;
 use crate::syscalls::SOURCE_GROUP_FLAG;
@@ -439,10 +443,7 @@ fn check_exec_big_offset_length() {
     }
 }
 
-#[test]
-fn check_type_id_one_in_one_out_resume() {
-    use std::collections::VecDeque;
-
+fn _check_type_id_one_in_one_out_resume(step_cycles: Cycle) -> Result<(), TestCaseError> {
     let script_version = SCRIPT_VERSION;
 
     let (always_success_cell, always_success_cell_data, always_success_script) =
@@ -501,16 +502,12 @@ fn check_type_id_one_in_one_out_resume() {
     verifier.verify_map(script_version, &rtx, |verifier| {
         let mut groups: VecDeque<_> = verifier.groups_with_type().collect();
         let mut tmp: Option<ResumableMachine<'_>> = None;
-        let mut step_cycles = match groups.front().unwrap().0 {
-            ScriptGroupType::Lock => ALWAYS_SUCCESS_SCRIPT_CYCLE,
-            ScriptGroupType::Type => TYPE_ID_CYCLES - 10,
-        };
+        let mut limit = step_cycles;
 
         loop {
             if let Some(mut vm) = tmp.take() {
-                cycles += vm.cycles();
-                vm.set_cycles(0);
-                match vm.machine.run() {
+                vm.set_max_cycles(limit);
+                match vm.run() {
                     Ok(code) => {
                         if code == 0 {
                             cycles += vm.cycles();
@@ -522,6 +519,7 @@ fn check_type_id_one_in_one_out_resume() {
                     Err(error) => match error {
                         VMInternalError::CyclesExceeded => {
                             tmp = Some(vm);
+                            limit += step_cycles;
                             continue;
                         }
                         _ => unreachable!(),
@@ -532,26 +530,33 @@ fn check_type_id_one_in_one_out_resume() {
                 break;
             }
 
-            while let Some((_ty, _, group)) = groups.front().cloned() {
+            while let Some((ty, _, group)) = groups.front().cloned() {
                 match verifier
-                    .verify_group_with_chunk(group, step_cycles, &None)
+                    .verify_group_with_chunk(group, limit, &None)
                     .unwrap()
                 {
                     ChunkState::Completed(used_cycles) => {
                         cycles += used_cycles;
                         groups.pop_front();
-                        if let Some(front) = groups.front() {
-                            step_cycles = match front.0 {
-                                ScriptGroupType::Lock => ALWAYS_SUCCESS_SCRIPT_CYCLE,
-                                ScriptGroupType::Type => TYPE_ID_CYCLES - 10,
-                            };
+                        if groups.front().is_some() {
+                            limit = step_cycles;
                         }
                     }
                     ChunkState::Suspended(vm) => {
                         if vm.is_some() {
                             tmp = vm;
+                        } else if ty == ScriptGroupType::Type // fast forward
+                            && step_cycles > TYPE_ID_CYCLES
+                            && limit < (TYPE_ID_CYCLES - step_cycles)
+                        {
+                            limit += TYPE_ID_CYCLES - step_cycles;
+                        } else if ty == ScriptGroupType::Lock  // fast forward
+                            && step_cycles < ALWAYS_SUCCESS_SCRIPT_CYCLE
+                            && limit < (ALWAYS_SUCCESS_SCRIPT_CYCLE - step_cycles)
+                        {
+                            limit += ALWAYS_SUCCESS_SCRIPT_CYCLE - step_cycles;
                         } else {
-                            step_cycles += 10
+                            limit += step_cycles;
                         }
                         break;
                     }
@@ -560,118 +565,30 @@ fn check_type_id_one_in_one_out_resume() {
         }
     });
 
-    assert_eq!(cycles, TYPE_ID_CYCLES + ALWAYS_SUCCESS_SCRIPT_CYCLE);
+    prop_assert_eq!(cycles, TYPE_ID_CYCLES + ALWAYS_SUCCESS_SCRIPT_CYCLE);
+    Ok(())
 }
 
-#[test]
-fn check_type_id_one_in_one_out_chunk() {
-    let script_version = SCRIPT_VERSION;
-
-    let (always_success_cell, always_success_cell_data, always_success_script) =
-        always_success_cell();
-    let always_success_out_point = OutPoint::new(h256!("0x11").pack(), 0);
-
-    let type_id_script = Script::new_builder()
-        .args(Bytes::from(h256!("0x1111").as_ref()).pack())
-        .code_hash(TYPE_ID_CODE_HASH.pack())
-        .hash_type(ScriptHashType::Type.into())
-        .build();
-
-    let input = CellInput::new(OutPoint::new(h256!("0x1234").pack(), 8), 0);
-    let input_cell = CellOutputBuilder::default()
-        .capacity(capacity_bytes!(1000).pack())
-        .lock(always_success_script.clone())
-        .type_(Some(type_id_script.clone()).pack())
-        .build();
-
-    let output_cell = CellOutputBuilder::default()
-        .capacity(capacity_bytes!(990).pack())
-        .lock(always_success_script.clone())
-        .type_(Some(type_id_script).pack())
-        .build();
-
-    let transaction = TransactionBuilder::default()
-        .input(input.clone())
-        .output(output_cell)
-        .cell_dep(
-            CellDep::new_builder()
-                .out_point(always_success_out_point.clone())
-                .build(),
-        )
-        .build();
-
-    let resolved_input_cell = CellMetaBuilder::from_cell_output(input_cell, Bytes::new())
-        .out_point(input.previous_output())
-        .build();
-    let resolved_always_success_cell = CellMetaBuilder::from_cell_output(
-        always_success_cell.clone(),
-        always_success_cell_data.to_owned(),
-    )
-    .out_point(always_success_out_point)
-    .build();
-
-    let rtx = ResolvedTransaction {
-        transaction,
-        resolved_cell_deps: vec![resolved_always_success_cell],
-        resolved_inputs: vec![resolved_input_cell],
-        resolved_dep_groups: vec![],
-    };
-
-    let mut cycles = 0;
-    let verifier = TransactionScriptsVerifierWithEnv::new();
-
-    verifier.verify_map(script_version, &rtx, |verifier| {
-        let mut groups: Vec<_> = verifier.groups_with_type().collect();
-        let mut tmp: Option<ResumableMachine<'_>> = None;
-
-        loop {
-            if let Some(mut vm) = tmp.take() {
-                cycles += vm.cycles();
-                vm.set_cycles(0);
-                match vm.machine.run() {
-                    Ok(code) => {
-                        if code == 0 {
-                            cycles += vm.cycles();
-                        } else {
-                            unreachable!()
-                        }
-                    }
-                    Err(error) => match error {
-                        VMInternalError::CyclesExceeded => {
-                            tmp = Some(vm);
-                            continue;
-                        }
-                        _ => unreachable!(),
-                    },
-                }
-            }
-            while let Some((ty, _, group)) = groups.pop() {
-                let max = match ty {
-                    ScriptGroupType::Lock => ALWAYS_SUCCESS_SCRIPT_CYCLE - 10,
-                    ScriptGroupType::Type => TYPE_ID_CYCLES,
-                };
-                match verifier.verify_group_with_chunk(group, max, &None).unwrap() {
-                    ChunkState::Completed(used_cycles) => {
-                        cycles += used_cycles;
-                    }
-                    ChunkState::Suspended(vm) => {
-                        tmp = vm;
-                        break;
-                    }
-                }
-            }
-
-            if tmp.is_none() {
-                break;
-            }
+// default is 256, which takes too long times
+proptest! {
+    #![proptest_config(ProptestConfig::with_cases(42))]
+    #[test]
+    fn check_type_id_one_in_one_out_resume1(step in 1..ALWAYS_SUCCESS_SCRIPT_CYCLE) {
+        if SCRIPT_VERSION >= ScriptVersion::V1 {
+            _check_type_id_one_in_one_out_resume(step)?;
         }
-    });
+    }
+}
 
-    assert_eq!(cycles, TYPE_ID_CYCLES + ALWAYS_SUCCESS_SCRIPT_CYCLE);
+proptest! {
+    #![proptest_config(ProptestConfig::with_cases(42))]
+    #[test]
+    fn check_type_id_one_in_one_out_resume2(step in ALWAYS_SUCCESS_SCRIPT_CYCLE..(ALWAYS_SUCCESS_SCRIPT_CYCLE + TYPE_ID_CYCLES)) {
+        _check_type_id_one_in_one_out_resume(step)?;
+    }
 }
 
-#[test]
-fn check_typical_secp256k1_blake160_2_in_2_out_tx_with_chunk() {
+fn _check_typical_secp256k1_blake160_2_in_2_out_tx_with_chunk(step_cycles: Cycle) {
     let script_version = SCRIPT_VERSION;
 
     let rtx = random_2_in_2_out_rtx();
@@ -681,12 +598,12 @@ fn check_typical_secp256k1_blake160_2_in_2_out_tx_with_chunk() {
     let result = verifier.verify_map(script_version, &rtx, |verifier| {
         let mut groups: Vec<_> = verifier.groups_with_type().collect();
         let mut tmp: Option<ResumableMachine<'_>> = None;
+        let mut limit = step_cycles;
 
         loop {
             if let Some(mut vm) = tmp.take() {
-                cycles += vm.cycles();
-                vm.set_cycles(0);
-                match vm.machine.run() {
+                vm.set_max_cycles(limit);
+                match vm.run() {
                     Ok(code) => {
                         if code == 0 {
                             cycles += vm.cycles();
@@ -697,6 +614,7 @@ fn check_typical_secp256k1_blake160_2_in_2_out_tx_with_chunk() {
                     Err(error) => match error {
                         VMInternalError::CyclesExceeded => {
                             tmp = Some(vm);
+                            limit += step_cycles;
                             continue;
                         }
                         _ => unreachable!(),
@@ -705,14 +623,19 @@ fn check_typical_secp256k1_blake160_2_in_2_out_tx_with_chunk() {
             }
             while let Some((_, _, group)) = groups.pop() {
                 match verifier
-                    .verify_group_with_chunk(group, TWO_IN_TWO_OUT_CYCLES / 10, &None)
+                    .verify_group_with_chunk(group, limit, &None)
                     .unwrap()
                 {
                     ChunkState::Completed(used_cycles) => {
                         cycles += used_cycles;
                     }
                     ChunkState::Suspended(vm) => {
                         tmp = vm;
+                        if limit < (TWO_IN_TWO_OUT_CYCLES - step_cycles) {
+                            limit += TWO_IN_TWO_OUT_CYCLES - step_cycles;
+                        } else {
+                            limit += step_cycles;
+                        }
                         break;
                     }
                 }
@@ -727,34 +650,49 @@ fn check_typical_secp256k1_blake160_2_in_2_out_tx_with_chunk() {
     });
 
     let cycles_once = result.unwrap();
-    assert!(cycles <= TWO_IN_TWO_OUT_CYCLES);
-    assert!(cycles >= TWO_IN_TWO_OUT_CYCLES - CYCLE_BOUND);
-    assert_eq!(cycles, cycles_once);
+    assert!(
+        cycles <= TWO_IN_TWO_OUT_CYCLES,
+        "step_cycles {}",
+        step_cycles
+    );
+    assert!(
+        cycles >= TWO_IN_TWO_OUT_CYCLES - CYCLE_BOUND,
+        "step_cycles {}",
+        step_cycles
+    );
+    assert_eq!(cycles, cycles_once, "step_cycles {}", step_cycles);
 }
 
 #[test]
-fn check_typical_secp256k1_blake160_2_in_2_out_tx_with_snap() {
+fn check_typical_secp256k1_blake160_2_in_2_out_tx_with_chunk() {
+    if SCRIPT_VERSION >= ScriptVersion::V1 {
+        let mut rng = thread_rng();
+        let step_cycles1 = rng.sample(Uniform::from(1..100u64));
+        _check_typical_secp256k1_blake160_2_in_2_out_tx_with_chunk(step_cycles1);
+
+        let step_cycles2 = rng.sample(Uniform::from(100u64..TWO_IN_TWO_OUT_CYCLES - CYCLE_BOUND));
+        _check_typical_secp256k1_blake160_2_in_2_out_tx_with_chunk(step_cycles2);
+    }
+}
+
+fn _check_typical_secp256k1_blake160_2_in_2_out_tx_with_state(step_cycles: Cycle) {
     let script_version = SCRIPT_VERSION;
 
     let rtx = random_2_in_2_out_rtx();
     let mut cycles = 0;
     let verifier = TransactionScriptsVerifierWithEnv::new();
     let result = verifier.verify_map(script_version, &rtx, |verifier| {
-        let mut init_snap: Option<TransactionSnapshot> = None;
+        let mut init_state: Option<TransactionState<'_>> = None;
 
-        if let VerifyResult::Suspended(state) = verifier
-            .resumable_verify(TWO_IN_TWO_OUT_CYCLES / 10)
-            .unwrap()
-        {
-            init_snap = Some(state.try_into().unwrap());
+        if let VerifyResult::Suspended(state) = verifier.resumable_verify(step_cycles).unwrap() {
+            init_state = Some(state);
         }
 
         loop {
-            let snap = init_snap.take().unwrap();
-            let (limit_cycles, _last) =
-                snap.next_limit_cycles(TWO_IN_TWO_OUT_CYCLES / 10, TWO_IN_TWO_OUT_CYCLES);
-            match verifier.resume_from_snap(&snap, limit_cycles).unwrap() {
-                VerifyResult::Suspended(state) => init_snap = Some(state.try_into().unwrap()),
+            let state = init_state.take().unwrap();
+            let (limit_cycles, _last) = state.next_limit_cycles(step_cycles, TWO_IN_TWO_OUT_CYCLES);
+            match verifier.resume_from_state(state, limit_cycles).unwrap() {
+                VerifyResult::Suspended(state) => init_state = Some(state),
                 VerifyResult::Completed(cycle) => {
                     cycles = cycle;
                     break;
@@ -766,48 +704,114 @@ fn check_typical_secp256k1_blake160_2_in_2_out_tx_with_snap() {
     });
 
     let cycles_once = result.unwrap();
-    assert!(cycles <= TWO_IN_TWO_OUT_CYCLES);
-    assert!(cycles >= TWO_IN_TWO_OUT_CYCLES - CYCLE_BOUND);
-    assert_eq!(cycles, cycles_once);
+    assert!(
+        cycles <= TWO_IN_TWO_OUT_CYCLES,
+        "step_cycles {}",
+        step_cycles
+    );
+    assert!(
+        cycles >= TWO_IN_TWO_OUT_CYCLES - CYCLE_BOUND,
+        "step_cycles {}",
+        step_cycles
+    );
+    assert_eq!(cycles, cycles_once, "step_cycles {}", step_cycles);
 }
 
 #[test]
 fn check_typical_secp256k1_blake160_2_in_2_out_tx_with_state() {
+    if SCRIPT_VERSION >= ScriptVersion::V1 {
+        let mut rng = thread_rng();
+        let step_cycles1 = rng.sample(Uniform::from(1..100u64));
+        _check_typical_secp256k1_blake160_2_in_2_out_tx_with_state(step_cycles1);
+
+        let step_cycles2 = rng.sample(Uniform::from(100u64..TWO_IN_TWO_OUT_CYCLES - CYCLE_BOUND));
+        _check_typical_secp256k1_blake160_2_in_2_out_tx_with_state(step_cycles2);
+    }
+}
+
+fn _check_typical_secp256k1_blake160_2_in_2_out_tx_with_snap(step_cycles: Cycle) {
     let script_version = SCRIPT_VERSION;
 
     let rtx = random_2_in_2_out_rtx();
     let mut cycles = 0;
     let verifier = TransactionScriptsVerifierWithEnv::new();
     let result = verifier.verify_map(script_version, &rtx, |verifier| {
+        let mut init_snap: Option<TransactionSnapshot> = None;
         let mut init_state: Option<TransactionState<'_>> = None;
 
-        if let VerifyResult::Suspended(state) = verifier
-            .resumable_verify(TWO_IN_TWO_OUT_CYCLES / 10)
-            .unwrap()
-        {
-            init_state = Some(state);
+        if let VerifyResult::Suspended(state) = verifier.resumable_verify(step_cycles).unwrap() {
+            init_snap = Some(state.try_into().unwrap());
         }
 
+        let mut count = 0;
         loop {
-            let state = init_state.take().unwrap();
-            let (limit_cycles, _last) =
-                state.next_limit_cycles(TWO_IN_TWO_OUT_CYCLES / 10, TWO_IN_TWO_OUT_CYCLES);
-            match verifier.resume_from_state(state, limit_cycles).unwrap() {
-                VerifyResult::Suspended(state) => init_state = Some(state),
-                VerifyResult::Completed(cycle) => {
-                    cycles = cycle;
-                    break;
+            if init_snap.is_some() {
+                let snap = init_snap.take().unwrap();
+                let (limit_cycles, _last) =
+                    snap.next_limit_cycles(step_cycles, TWO_IN_TWO_OUT_CYCLES);
+                match verifier.resume_from_snap(&snap, limit_cycles).unwrap() {
+                    VerifyResult::Suspended(state) => {
+                        if count % 500 == 0 {
+                            init_snap = Some(state.try_into().unwrap());
+                        } else {
+                            init_state = Some(state);
+                        }
+                    }
+                    VerifyResult::Completed(cycle) => {
+                        cycles = cycle;
+                        break;
+                    }
+                }
+            } else {
+                let state = init_state.take().unwrap();
+                let (limit_cycles, _last) =
+                    state.next_limit_cycles(step_cycles, TWO_IN_TWO_OUT_CYCLES);
+                match verifier.resume_from_state(state, limit_cycles).unwrap() {
+                    VerifyResult::Suspended(state) => {
+                        if count % 500 == 0 {
+                            init_snap = Some(state.try_into().unwrap());
+                        } else {
+                            init_state = Some(state);
+                        }
+                    }
+                    VerifyResult::Completed(cycle) => {
+                        cycles = cycle;
+                        break;
+                    }
                 }
             }
+            count += 1;
         }
 
         verifier.verify(TWO_IN_TWO_OUT_CYCLES)
     });
 
     let cycles_once = result.unwrap();
-    assert!(cycles <= TWO_IN_TWO_OUT_CYCLES);
-    assert!(cycles >= TWO_IN_TWO_OUT_CYCLES - CYCLE_BOUND);
-    assert_eq!(cycles, cycles_once);
+    assert!(
+        cycles <= TWO_IN_TWO_OUT_CYCLES,
+        "step_cycles {}",
+        step_cycles
+    );
+    assert!(
+        cycles >= TWO_IN_TWO_OUT_CYCLES - CYCLE_BOUND,
+        "step_cycles {}",
+        step_cycles
+    );
+    assert_eq!(cycles, cycles_once, "step_cycles {}", step_cycles);
+}
+
+#[test]
+fn check_typical_secp256k1_blake160_2_in_2_out_tx_with_snap() {
+    if SCRIPT_VERSION >= ScriptVersion::V1 {
+        let mut rng = thread_rng();
+        let step_cycles1 = rng.sample(Uniform::from(1..100u64));
+        _check_typical_secp256k1_blake160_2_in_2_out_tx_with_snap(step_cycles1);
+
+        let step_cycles2 = rng.sample(Uniform::from(
+            TWO_IN_TWO_OUT_CYCLES / 10..TWO_IN_TWO_OUT_CYCLES - CYCLE_BOUND,
+        ));
+        _check_typical_secp256k1_blake160_2_in_2_out_tx_with_snap(step_cycles2);
+    }
 }
 
 #[test]
```
