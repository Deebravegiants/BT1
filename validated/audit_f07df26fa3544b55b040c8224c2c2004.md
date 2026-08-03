No vulnerability found for this question.

The `AbortedDependencies::add_stall`/`remove_stall` disjointness invariant is enforced structurally: `record_dependencies` only inserts into `not_stalled_deps` when the id isn't already in `stalled_deps` [1](#0-0) , and `add_stall`/`remove_stall` move elements wholesale between the two sets via `BTreeSet::append`, with `#[cfg(test)]` assertions checking disjointness on every call [2](#0-1) [3](#0-2) . All access to a given `AbortedDependencies` instance is serialized through a per-transaction `Mutex` held for the duration of `propagate`'s add/remove-stall call [4](#0-3) , so there is no concurrent interleaving within a single instance that could violate the invariant; extensive unit tests (`stall_aborted_dependencies`, `remove_stall_aborted_dependencies`, `propagate`, `remove_stall_propagation_scenario`) exercise these exact sequences and confirm the invariant holds [5](#0-4) [6](#0-5) .

More fundamentally, this stall mechanism is explicitly documented as a "best-effort" scheduling heuristic used only to decide when to defer re-execution/scheduling of transactions in the parallel execution engine (BlockSTMv2), not a mechanism that determines final authorization, ownership, or committed transaction outcomes [7](#0-6) . Actual correctness of committed results (including any Move-level object/capability checks such as a token's burn ref) is enforced independently through BlockSTM's read-set validation and the Move VM's authorization semantics, not through this stall bookkeeping. There is no code path by which a scheduler-internal stall/dependency-tracking bug could cause an unprivileged party to bypass a `BurnRef`/capability check on a token object — the review requires a real custody-boundary crossing tied to Move-level ownership/authority, and this scheduler logic has no such linkage.

### Citations

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L298-304)
```rust
    fn record_dependencies(&mut self, dependencies: impl Iterator<Item = TxnIndex>) {
        for dep in dependencies {
            if !self.stalled_deps.contains(&dep) {
                self.not_stalled_deps.insert(dep);
            }
        }
    }
```

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L313-327)
```rust
        for idx in &self.not_stalled_deps {
            // Assert the invariant in tests.
            #[cfg(test)]
            assert!(!self.stalled_deps.contains(idx));

            if statuses.add_stall(*idx)? {
                // May require recursive add_stalls.
                stall_propagation_queue.insert(*idx as usize);
            }
        }

        self.stalled_deps.append(&mut self.not_stalled_deps);
        self.is_stalled = true;
        Ok(())
    }
```

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L338-352)
```rust
        for idx in &self.stalled_deps {
            // Assert the invariant in tests.
            #[cfg(test)]
            assert!(!self.not_stalled_deps.contains(idx));

            if statuses.remove_stall(*idx)? {
                // May require recursive remove_stalls.
                stall_propagation_queue.insert(*idx as usize);
            }
        }

        self.not_stalled_deps.append(&mut self.stalled_deps);
        self.is_stalled = false;
        Ok(())
    }
```

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L1247-1265)
```rust
        while let Some(task_idx) = stall_propagation_queue.pop_first() {
            // Make sure the conditions are checked under dependency lock.
            let mut aborted_deps_guard = self.aborted_dependencies[task_idx].lock();

            // Checks the current status to determine whether to propagate add / remove stall,
            // calling which only affects its currently not_stalled (or stalled) dependencies.
            // Allows to store indices in propagation queue (not add or remove commands) & avoids
            // handling corner cases such as merging commands (as propagation process is not atomic).
            if self
                .txn_statuses
                .shortcut_executed_and_not_stalled(task_idx)
            {
                // Still makes sense to propagate remove_stall.
                aborted_deps_guard
                    .remove_stall(&self.txn_statuses, &mut stall_propagation_queue)?;
            } else {
                // Not executed or stalled - still makes sense to propagate add_stall.
                aborted_deps_guard.add_stall(&self.txn_statuses, &mut stall_propagation_queue)?;
            }
```

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L1419-1489)
```rust
    #[test]
    fn stall_aborted_dependencies() {
        let mut stall_propagation_queue = BTreeSet::new();

        // num_txns is 6.
        let statuses =
            ExecutionStatuses::new_for_test(ExecutionQueueManager::new_for_test(6), vec![
                ExecutionStatus::new(),
                ExecutionStatus::new(),
                // Statuses for txn_idx 2, 3, 4 have incarnation > 0 and different inner status.
                ExecutionStatus::new_for_test(
                    StatusWithIncarnation::new_for_test(SchedulingStatus::PendingScheduling, 1),
                    0,
                ),
                ExecutionStatus::new_for_test(
                    StatusWithIncarnation::new_for_test(
                        SchedulingStatus::Executing(BTreeSet::new()),
                        1,
                    ),
                    0,
                ),
                ExecutionStatus::new_for_test(
                    StatusWithIncarnation::new_for_test(SchedulingStatus::Executed, 1),
                    0,
                ),
                // Status for txn 5 is already stalled.
                ExecutionStatus::new_for_test(
                    StatusWithIncarnation::new_for_test(SchedulingStatus::PendingScheduling, 1),
                    1,
                ),
            ]);
        assert_eq!(statuses.len(), 6);
        let manager = &statuses.get_execution_queue_manager();
        let mut deps = AbortedDependencies::new();

        assert!(!deps.is_stalled);
        assert_ok!(deps.add_stall(&statuses, &mut stall_propagation_queue));
        assert!(deps.is_stalled);
        deps.not_stalled_deps.insert(0);
        // Err because of incarnation 0.
        assert_err!(deps.add_stall(&statuses, &mut stall_propagation_queue));
        // From now on, mark 0 as already stalled.
        assert!(deps.stalled_deps.insert(0));
        assert!(deps.not_stalled_deps.remove(&0));

        // Successful stall when status requires execution must remove 2 from execution
        // queue, while different status or unsuccessful stall should not.
        manager.execution_queue.lock().clear();
        manager.execution_queue.lock().append(&mut (2..6).collect());
        deps.not_stalled_deps.append(&mut (2..6).collect());
        assert_ok!(deps.add_stall(&statuses, &mut stall_propagation_queue));

        // Check the results: execution queue, propagation_queue, deps.stalled & not_stalled.
        assert_eq!(manager.execution_queue.lock().len(), 3);
        for i in 3..6 {
            assert!(manager.execution_queue.lock().contains(&i));
        }

        // 5 is not in the propagation queue because it was already stalled.
        assert_eq!(stall_propagation_queue.len(), 3);
        for i in 2..5 {
            assert!(stall_propagation_queue.contains(&i));
        }

        assert_eq!(deps.stalled_deps.len(), 5);
        assert_eq!(deps.not_stalled_deps.len(), 0);
        assert!(deps.stalled_deps.contains(&0)); // pre-inserted
        for i in 2..6 {
            assert!(deps.stalled_deps.contains(&i));
        }
    }
```

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L1491-1582)
```rust
    #[test]
    fn remove_stall_aborted_dependencies() {
        let mut stall_propagation_queue = BTreeSet::new();

        // num_txns is 8.
        let mut statuses =
            ExecutionStatuses::new_for_test(ExecutionQueueManager::new_for_test(6), vec![
                ExecutionStatus::new_for_test(
                    StatusWithIncarnation::new_for_test(SchedulingStatus::PendingScheduling, 1),
                    0,
                ),
                ExecutionStatus::new(),
                // For the next 3 statuses, executed_once_max_idx will be >= their
                // indices. Only 4 should be add to execution queue, as 2 and 3 do
                // not require execution. All should be added to propagation queue.
                ExecutionStatus::new_for_test(
                    StatusWithIncarnation::new_for_test(
                        SchedulingStatus::Executing(BTreeSet::new()),
                        1,
                    ),
                    1,
                ),
                ExecutionStatus::new_for_test(
                    StatusWithIncarnation::new_for_test(SchedulingStatus::Executed, 1),
                    1,
                ),
                ExecutionStatus::new_for_test(
                    StatusWithIncarnation::new_for_test(SchedulingStatus::PendingScheduling, 1),
                    1,
                ),
                // For below statuses, executed_once_max_idx will be < their indices:
                // we will test is_first_incarnation behavior.
                ExecutionStatus::new_for_test(
                    StatusWithIncarnation::new_for_test(SchedulingStatus::PendingScheduling, 1),
                    1,
                ),
                ExecutionStatus::new_for_test(
                    StatusWithIncarnation::new_for_test(SchedulingStatus::PendingScheduling, 2),
                    1,
                ),
                // Should not be added to the queues, as num_stalls = 2 (status
                // remains stalled after call).
                ExecutionStatus::new_for_test(
                    StatusWithIncarnation::new_for_test(SchedulingStatus::PendingScheduling, 2),
                    2,
                ),
            ]);
        let mut deps = AbortedDependencies::new();
        assert_eq!(statuses.len(), 8);

        deps.is_stalled = true;
        assert_ok!(deps.remove_stall(&statuses, &mut stall_propagation_queue));
        assert!(!deps.is_stalled);
        deps.stalled_deps.insert(0);
        // Removing stall should fail because num_stalls = 0.
        assert_err!(deps.remove_stall(&statuses, &mut stall_propagation_queue));
        *statuses.get_status_mut(0) = ExecutionStatus::new_for_test(
            StatusWithIncarnation::new_for_test(SchedulingStatus::PendingScheduling, 0),
            1,
        );
        // Removing stall should fail because incarnation = 0.
        assert_err!(deps.remove_stall(&statuses, &mut stall_propagation_queue));

        let manager = &statuses.get_execution_queue_manager();
        manager.executed_once_max_idx.store(4, Ordering::Relaxed);

        // From now on, ignore status for index 0 (mark as not_stalled):
        assert!(deps.not_stalled_deps.insert(0));
        assert!(deps.stalled_deps.remove(&0));

        manager.execution_queue.lock().clear();
        deps.stalled_deps.append(&mut (2..8).collect());
        assert_ok!(deps.remove_stall(&statuses, &mut stall_propagation_queue,));

        // Check the results: scheduling queue, propagation_queue, deps.stalled & not_stalled.
        assert_eq!(manager.execution_queue.lock().len(), 2);
        for i in [4, 6].iter() {
            assert!(manager.execution_queue.lock().contains(i));
        }

        assert_eq!(stall_propagation_queue.len(), 5);
        for i in 2..7 {
            stall_propagation_queue.contains(&i);
        }

        assert_eq!(deps.stalled_deps.len(), 0);
        assert_eq!(deps.not_stalled_deps.len(), 7);
        assert!(deps.not_stalled_deps.contains(&0)); // pre-inserted
        for i in 2..8 {
            assert!(deps.not_stalled_deps.contains(&i));
        }
    }
```

**File:** aptos-move/block-executor/src/scheduler_status.rs (L99-110)
```rust
Key aspects of the stall mechanism:

1. Purpose:
   - Records that a transaction has dependencies that are more likely to cause re-execution
   - Can be used to:
     a) Avoid scheduling transactions for re-execution until stalls are removed
     b) Guide handling when another transaction observes a dependency during execution
   - Helps constrain optimistic concurrency by limiting cascading aborts

2. Behavior:
   - Best-effort approach that allows flexibility in concurrency scenarios, but such that
     high-priority transactions may still be re-executed even in stalled state
```
