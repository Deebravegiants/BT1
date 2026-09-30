# [?] fix overflows

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-06-08
Source: https://github.com/nervosnetwork/ckb/commit/96475026fb496b40afcc76773b240afb3aabb846
Type: security-commit

## Details
fix overflows

## Patch
### Cargo.lock
```diff
@@ -1942,6 +1942,7 @@ dependencies = [
  "ckb-types",
  "ckb-util",
  "ckb-verification",
+ "futures-util",
  "http-body-util",
  "hyper",
  "hyper-util",
```

### chain/src/init_load_unverified.rs
```diff
@@ -3,7 +3,7 @@ use crate::{ChainController, LonelyBlock};
 use ckb_constant::sync::BLOCK_DOWNLOAD_WINDOW;
 use ckb_db::{Direction, IteratorMode};
 use ckb_db_schema::COLUMN_NUMBER_HASH;
-use ckb_logger::info;
+use ckb_logger::{error, info};
 use ckb_shared::Shared;
 use ckb_stop_handler::has_received_stop_signal;
 use ckb_store::ChainStore;
@@ -81,7 +81,14 @@ impl InitLoadUnverified {
             1,
             tip_number.saturating_sub(EXPIRED_EPOCH * self.shared.consensus().max_epoch_length()),
         );
-        let end_check_number = tip_number + BLOCK_DOWNLOAD_WINDOW * 10;
+        let Some(end_check_number) = tip_number.checked_add(BLOCK_DOWNLOAD_WINDOW * 10) else {
+            error!(
+                "unverified block scan end overflows: tip_number {}, window {}",
+                tip_number,
+                BLOCK_DOWNLOAD_WINDOW * 10
+            );
+            return;
+        };
 
         for check_unverified_number in start_check_number..=end_check_number {
             if has_received_stop_signal() {
```

### chain/src/verify.rs
```diff
@@ -24,8 +24,10 @@ use ckb_verification::cache::Completed;
 use ckb_verification_contextual::{ContextualBlockVerifier, VerifyContext};
 use ckb_verification_traits::Switch;
 use dashmap::DashSet;
+use std::any::Any;
 use std::cmp;
 use std::collections::HashSet;
+use std::panic::{AssertUnwindSafe, catch_unwind};
 use std::sync::Arc;
 
 pub(crate) struct ConsumeUnverifiedBlockProcessor {
@@ -79,7 +81,19 @@ impl ConsumeUnverifiedBlocks {
                         let _ = self.tx_pool_controller.suspend_chunk_process();
 
                         let _trace_now = minstant::Instant::now();
-                        self.processor.consume_unverified_blocks(unverified_task);
+                        let block_hash = unverified_task.block.hash();
+                        let block_number = unverified_task.block.number();
+                        if let Err(payload) = catch_unwind(AssertUnwindSafe(|| {
+                            self.processor.consume_unverified_blocks(unverified_task);
+                        })) {
+                            error!(
+                                "consume unverified block {}-{} panicked: {}",
+                                block_number,
+                                block_hash,
+                                panic_payload_to_string(payload.as_ref())
+                            );
+                            self.processor.is_pending_verify.remove(&block_hash);
+                        }
                         if let Some(handle) = ckb_metrics::handle() {
                             handle.ckb_chain_consume_unverified_block_duration.observe(_trace_now.elapsed().as_secs_f64())
                         }
@@ -893,6 +907,16 @@ impl ConsumeUnverifiedBlockProcessor {
     }
 }
 
+fn panic_payload_to_string(payload: &(dyn Any + Send)) -> String {
+    if let Some(message) = payload.downcast_ref::<&str>() {
+        (*message).to_owned()
+    } else if let Some(message) = payload.downcast_ref::<String>() {
+        message.clone()
+    } else {
+        "non-string panic payload".to_owned()
+    }
+}
+
 #[cfg(debug_assertions)]
 fn is_sorted_assert(fork: &ForkChanges) {
     assert!(fork.is_sorted())
```

### rpc/src/tests/fee_rate.rs
```diff
@@ -114,3 +114,30 @@ fn test_fee_rate_statics() {
         })
     );
 }
+
+#[test]
+fn test_fee_rate_statics_handles_large_values() {
+    let mut provider = DummyFeeRateProvider::new(3);
+    for i in 1..=2 {
+        provider.append(
+            i,
+            BlockExt {
+                received_at: 0,
+                total_difficulty: 0u64.into(),
+                total_uncles_count: 0,
+                verified: None,
+                txs_fees: vec![Capacity::shannons(u64::MAX)],
+                cycles: Some(vec![0]),
+                txs_sizes: Some(vec![0, 1]),
+            },
+        );
+    }
+
+    assert_eq!(
+        FeeRateCollector::new(&provider).statistics(Some(3)),
+        Some(FeeRateStatistics {
+            mean: u64::MAX.into(),
+            median: u64::MAX.into(),
+        })
+    );
+}
```

### rpc/src/util/fee_rate.rs
```diff
@@ -12,8 +12,9 @@ fn is_even(n: u64) -> bool {
 }
 
 fn mean(numbers: &[u64]) -> u64 {
-    let sum: u64 = numbers.iter().sum();
-    sum / numbers.len() as u64
+    // The average of u64 values fits in u64, but the intermediate sum may not.
+    let sum: u128 = numbers.iter().map(|number| u128::from(*number)).sum();
+    (sum / numbers.len() as u128) as u64
 }
 
 fn median(numbers: &mut [u64]) -> u64 {
```

### script/src/scheduler.rs
```diff
@@ -690,7 +690,10 @@ where
                     let copy_length = u64::min(full_length, real_length);
                     for i in 0..copy_length {
                         let fd = inherited_fd[i as usize].0;
-                        let addr = buffer_addr.checked_add(i * 8).ok_or(Error::MemOutOfBound)?;
+                        let offset = i.checked_mul(8).ok_or(Error::MemOutOfBound)?;
+                        let addr = buffer_addr
+                            .checked_add(offset)
+                            .ok_or(Error::MemOutOfBound)?;
                         machine
                             .inner_mut()
                             .memory_mut()
@@ -810,10 +813,12 @@ where
                 write_machine
                     .inner_mut()
                     .add_cycles_no_checking(transferred_byte_cycles(copiable))?;
-                let data = write_machine
-                    .inner_mut()
-                    .memory_mut()
-                    .load_bytes(write_buffer_addr.wrapping_add(consumed), copiable)?;
+                let data = write_machine.inner_mut().memory_mut().load_bytes(
+                    write_buffer_addr
+                        .checked_add(consumed)
+                        .ok_or(Error::MemOutOfBound)?,
+                    copiable,
+                )?;
                 let (_, read_machine) = self
                     .instantiated
                     .get_mut(&read_vm_id)
```

### script/src/syscalls/debugger.rs
```diff
@@ -1,7 +1,10 @@
 use crate::types::{
     DebugPrinter, {SgData, SgInfo},
 };
-use crate::{cost_model::transferred_byte_cycles, syscalls::DEBUG_PRINT_SYSCALL_NUMBER};
+use crate::{
+    cost_model::transferred_byte_cycles,
+    syscalls::{DEBUG_PRINT_SYSCALL_NUMBER, utils::checked_add_addr},
+};
 use ckb_vm::{
     Error as VMError, Memory, Register, SupportMachine, Syscalls,
     registers::{A0, A7},
@@ -45,7 +48,7 @@ impl<Mac: SupportMachine> Syscalls<Mac> for Debugger {
                 break;
             }
             buffer.push(byte);
-            addr += 1;
+            addr = checked_add_addr(addr, 1)?;
         }
 
         machine.add_cycles_no_checking(transferred_byte_cycles(buffer.len() as u64))?;
```

### script/src/syscalls/exec.rs
```diff
@@ -1,7 +1,7 @@
 use crate::cost_model::transferred_byte_cycles;
 use crate::syscalls::{
     EXEC, INDEX_OUT_OF_BOUND, MAX_ARGV_LENGTH, Place, SLICE_OUT_OF_BOUND, Source, SourceEntry,
-    WRONG_FORMAT,
+    WRONG_FORMAT, utils::checked_add_addr,
 };
 use crate::types::SgData;
 use ckb_traits::CellDataProvider;
@@ -169,7 +169,7 @@ impl<Mac: SupportMachine, DL: CellDataProvider + Send + Sync + Clone> Syscalls<M
                 return Err(VMError::Unexpected(ARGV_TOO_LONG_TEXT.to_string()));
             }
 
-            addr += 8;
+            addr = checked_add_addr(addr, 8)?;
         }
 
         let cycles = machine.cycles();
```

### script/src/syscalls/pipe.rs
```diff
@@ -1,4 +1,4 @@
-use crate::syscalls::{PIPE, SPAWN_YIELD_CYCLES_BASE};
+use crate::syscalls::{PIPE, SPAWN_YIELD_CYCLES_BASE, utils::checked_add_addr};
 use crate::types::{Message, PipeArgs, VmContext, VmId};
 use ckb_traits::{CellDataProvider, ExtensionProvider, HeaderProvider};
 use ckb_vm::{
@@ -35,7 +35,7 @@ impl<Mac: SupportMachine> Syscalls<Mac> for Pipe {
             return Ok(false);
         }
         let fd1_addr = machine.registers()[A0].to_u64();
-        let fd2_addr = fd1_addr.wrapping_add(8);
+        let fd2_addr = checked_add_addr(fd1_addr, 8)?;
         machine.add_cycles_no_checking(SPAWN_YIELD_CYCLES_BASE)?;
         self.message_box
             .lock()
```

### script/src/syscalls/spawn.rs
```diff
@@ -1,6 +1,6 @@
 use crate::syscalls::{
     INDEX_OUT_OF_BOUND, SLICE_OUT_OF_BOUND, SOURCE_ENTRY_MASK, SOURCE_GROUP_FLAG, SPAWN,
-    SPAWN_EXTRA_CYCLES_BASE, SPAWN_YIELD_CYCLES_BASE, Source,
+    SPAWN_EXTRA_CYCLES_BASE, SPAWN_YIELD_CYCLES_BASE, Source, utils::checked_add_addr,
 };
 use crate::types::{DataLocation, DataPieceId, Fd, Message, SgData, SpawnArgs, VmContext, VmId};
 use ckb_traits::{CellDataProvider, ExtensionProvider, HeaderProvider};
@@ -74,16 +74,16 @@ where
         let argc = machine
             .memory_mut()
             .load64(&Mac::REG::from_u64(argc_addr))?;
-        let argv_addr = spgs_addr.wrapping_add(8);
+        let argv_addr = checked_add_addr(spgs_addr, 8)?;
         let argv = machine
             .memory_mut()
             .load64(&Mac::REG::from_u64(argv_addr))?;
-        let process_id_addr_addr = spgs_addr.wrapping_add(16);
+        let process_id_addr_addr = checked_add_addr(spgs_addr, 16)?;
         let process_id_addr = machine
             .memory_mut()
             .load64(&Mac::REG::from_u64(process_id_addr_addr))?
             .to_u64();
-        let fds_addr_addr = spgs_addr.wrapping_add(24);
+        let fds_addr_addr = checked_add_addr(spgs_addr, 24)?;
         let mut fds_addr = machine
             .memory_mut()
             .load64(&Mac::REG::from_u64(fds_addr_addr))?
@@ -100,7 +100,7 @@ where
                     break;
                 }
                 fds.push(Fd(fd));
-                fds_addr += 8;
+                fds_addr = checked_add_addr(fds_addr, 8)?;
             }
         }
 
```

### script/src/syscalls/tests/mod.rs
```diff
@@ -13,3 +13,12 @@ mod vm_version_1;
 fn test_max_argv_length() {
     assert!(crate::syscalls::MAX_ARGV_LENGTH < u64::MAX);
 }
+
+#[test]
+fn test_checked_add_addr() {
+    assert_eq!(super::utils::checked_add_addr(7, 8), Ok(15));
+    assert!(matches!(
+        super::utils::checked_add_addr(u64::MAX, 1),
+        Err(ckb_vm::Error::MemOutOfBound)
+    ));
+}
```

### script/src/syscalls/tests/vm_latest/syscalls_2.rs
```diff
@@ -70,6 +70,101 @@ fn test_current_cycles() {
     assert_eq!(machine.registers()[A0], cycles);
 }
 
+#[test]
+fn test_pipe_fd_address_overflow() {
+    let mut machine = SCRIPT_VERSION.init_core_machine_without_limit();
+
+    machine.set_register(A0, u64::MAX);
+    machine.set_register(A7, PIPE);
+
+    let rtx = Arc::new(ResolvedTransaction {
+        transaction: TransactionBuilder::default().build(),
+        resolved_cell_deps: vec![],
+        resolved_inputs: vec![],
+        resolved_dep_groups: vec![],
+    });
+    let sg_data = build_sg_data(rtx, vec![], vec![]);
+    let vm_context = VmContext::new(&sg_data, &Arc::new(Mutex::new(Vec::new())));
+    let mut pipe = Pipe::new(&0, &vm_context);
+
+    assert!(matches!(
+        pipe.ecall(&mut machine),
+        Err(ckb_vm::Error::MemOutOfBound)
+    ));
+}
+
+#[test]
+fn test_spawn_args_address_out_of_bound() {
+    let mut machine = SCRIPT_VERSION.init_core_machine_without_limit();
+
+    machine.set_register(A0, 0);
+    machine.set_register(A1, u64::from(Source::Transaction(SourceEntry::CellDep)));
+    machine.set_register(A2, 0);
+    machine.set_register(A3, 0);
+    machine.set_register(A4, u64::MAX);
+    machine.set_register(A7, SPAWN);
+
+    let rtx = Arc::new(ResolvedTransaction {
+        transaction: TransactionBuilder::default().build(),
+        resolved_cell_deps: vec![],
+        resolved_inputs: vec![],
+        resolved_dep_groups: vec![],
+    });
+    let sg_data = build_sg_data(rtx, vec![], vec![]);
+    let vm_context = VmContext::new(&sg_data, &Arc::new(Mutex::new(Vec::new())));
+    let mut spawn = Spawn::new(&0, &vm_context);
+
+    assert!(matches!(
+        spawn.ecall(&mut machine),
+        Err(ckb_vm::Error::MemOutOfBound)
+    ));
+}
+
+#[test]
+fn test_spawn_inherited_fds_address_out_of_bound() {
+    let mut machine = SCRIPT_VERSION.init_core_machine_without_limit();
+    let spawn_args_addr = 0;
+
+    machine
+        .memory_mut()
+        .store64(&spawn_args_addr, &0)
+        .expect("store argc");
+    machine
+        .memory_mut()
+        .store64(&(spawn_args_addr + 8), &0)
+        .expect("store argv");
+    machine
+        .memory_mut()
+        .store64(&(spawn_args_addr + 16), &0)
+        .expect("store process_id");
+    machine
+        .memory_mut()
+        .store64(&(spawn_args_addr + 24), &u64::MAX)
+        .expect("store inherited_fds");
+
+    machine.set_register(A0, 0);
+    machine.set_register(A1, u64::from(Source::Transaction(SourceEntry::CellDep)));
+    machine.set_register(A2, 0);
+    machine.set_register(A3, 0);
+    machine.set_register(A4, spawn_args_addr);
+    machine.set_register(A7, SPAWN);
+
+    let rtx = Arc::new(ResolvedTransaction {
+        transaction: TransactionBuilder::default().build(),
+        resolved_cell_deps: vec![],
+        resolved_inputs: vec![],
+        resolved_dep_groups: vec![],
+    });
+    let sg_data = build_sg_data(rtx, vec![], vec![]);
+    let vm_context = VmContext::new(&sg_data, &Arc::new(Mutex::new(Vec::new())));
+    let mut spawn = Spawn::new(&0, &vm_context);
+
+    assert!(matches!(
+        spawn.ecall(&mut machine),
+        Err(ckb_vm::Error::MemOutOfBound)
+    ));
+}
+
 fn _test_load_extension(
     data: &[u8],
     index: u64,
```
