# [?] fix(node-rewards-canister): Fixes sync task not being rescheduled due to possible panic in closure (#9352)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-03-17
Source: https://github.com/dfinity/ic/commit/0831b63996d90143aa232448c02ae60fdafd5975
Type: security-commit

## Details
fix(node-rewards-canister): Fixes sync task not being rescheduled due to possible panic in closure (#9352)

This PR adds a recovery timer mechanism to ensure tasks are rescheduled
after a possible panic in the execution of the task.
This is done scheduling first a timer which reschedules the task itself
after sometime (15 min). If the task execution is successful the first
timer will be cancelled and the task rescheduled after chosen delay.
This fixes https://dfinity.atlassian.net/browse/SECFIND-2110

---------

Co-authored-by: IDX GitHub Automation <infra+github-automation@dfinity.org>

## Patch
### rs/node_rewards/canister/src/main.rs
```diff
@@ -75,6 +75,30 @@ fn get_registry_value(key: String) -> Result<Option<Vec<u8>>, String> {
     CANISTER.with(|canister| canister.borrow().get_registry_value(key))
 }
 
+#[cfg(feature = "test")]
+#[query(hidden = true)]
+fn __self_call() {}
+
+#[cfg(feature = "test")]
+#[update(hidden = true)]
+fn start_recovery_test_tasks() {
+    use ic_node_rewards_canister::timer_tasks::test_tasks::{
+        PanickingRecoveryTask, SuccessRecoveryTask,
+    };
+    PanickingRecoveryTask.schedule();
+    SuccessRecoveryTask.schedule();
+}
+
+#[cfg(feature = "test")]
+#[query(hidden = true)]
+fn get_recovery_test_counters() -> (u64, u64) {
+    use ic_node_rewards_canister::timer_tasks::test_tasks;
+    (
+        test_tasks::get_success_task_counter(),
+        test_tasks::get_panic_task_counter(),
+    )
+}
+
 #[update]
 async fn get_node_providers_monthly_xdr_rewards(
     request: GetNodeProvidersMonthlyXdrRewardsRequest,
```

### rs/node_rewards/canister/src/timer_tasks.rs
```diff
@@ -6,6 +6,7 @@ use chrono::{DateTime, Days, NaiveDate};
 use futures::FutureExt;
 #[cfg(target_arch = "wasm32")]
 use ic_cdk::futures::spawn;
+use ic_cdk_timers::clear_timer;
 use ic_nervous_system_common::ONE_DAY_SECONDS;
 use ic_nervous_system_timer_task::{RecurringSyncTask, set_timer};
 use ic_node_rewards_canister_api::DateUtc;
@@ -38,15 +39,30 @@ fn spawn_in_canister_env(future: impl Future<Output = ()> + Sized + 'static) {
 }
 
 #[async_trait(?Send)]
-pub trait RecurringAsyncTaskNonSend: Sized + 'static {
+pub trait RecurringAsyncTaskNonSend: Clone + Sized + 'static {
     async fn execute(self) -> (Duration, Self);
     fn initial_delay(&self) -> Duration;
+    fn recovery_delay(&self) -> Duration;
 
     fn schedule_with_delay(self, delay: Duration) {
         set_timer(delay, async move {
+            // Set a recovery timer before spawning the task. The timer callback
+            // and the spawned future run in different IC messages, so if the
+            // spawned future traps, the recovery timer survives and will reschedule the task.
+            let recovery = self.clone();
+            let recovery_delay = recovery.recovery_delay();
+            let recovery_timer_id = set_timer(recovery_delay, async move {
+                ic_cdk::println!(
+                    "Task {} recovery timer fired — rescheduling after suspected trap.",
+                    Self::NAME,
+                );
+                recovery.schedule_with_delay(recovery_delay);
+            });
+
             spawn_in_canister_env(async move {
                 let (new_delay, new_task) = self.execute().await;
 
+                clear_timer(recovery_timer_id);
                 new_task.schedule_with_delay(new_delay);
             });
         });
@@ -121,6 +137,11 @@ impl RecurringAsyncTaskNonSend for HourlySyncTask {
     fn initial_delay(&self) -> Duration {
         Duration::from_secs(0)
     }
+
+    fn recovery_delay(&self) -> Duration {
+        Duration::from_secs(RETRY_FAILED_SYNC_SECS)
+    }
+
     const NAME: &'static str = "hourly_sync";
 }
 
@@ -184,3 +205,77 @@ pub fn yesterday() -> NaiveDate {
         .pred_opt()
         .unwrap()
 }
+
+#[cfg(feature = "test")]
+pub mod test_tasks {
+    use super::*;
+    use std::cell::Cell;
+
+    const RECOVERY_DELAY_SECS: u64 = 10;
+    const SUCCESS_TASK_DELAY_SECS: u64 = 5;
+
+    thread_local! {
+        static PANIC_TASK_COUNTER: Cell<u64> = const { Cell::new(0) };
+        static SUCCESS_TASK_COUNTER: Cell<u64> = const { Cell::new(0) };
+    }
+
+    pub fn get_panic_task_counter() -> u64 {
+        PANIC_TASK_COUNTER.with(|c| c.get())
+    }
+
+    pub fn get_success_task_counter() -> u64 {
+        SUCCESS_TASK_COUNTER.with(|c| c.get())
+    }
+
+    #[derive(Clone)]
+    pub struct PanickingRecoveryTask;
+
+    #[async_trait(?Send)]
+    impl RecurringAsyncTaskNonSend for PanickingRecoveryTask {
+        async fn execute(self) -> (Duration, Self) {
+            PANIC_TASK_COUNTER.with(|c| c.set(c.get() + 1));
+
+            ic_cdk::call::Call::unbounded_wait(ic_cdk::api::canister_self(), "__self_call")
+                .await
+                .unwrap();
+
+            panic!("intentional panic for recovery timer test");
+        }
+
+        fn initial_delay(&self) -> Duration {
+            Duration::from_secs(0)
+        }
+
+        fn recovery_delay(&self) -> Duration {
+            Duration::from_secs(RECOVERY_DELAY_SECS)
+        }
+
+        const NAME: &'static str = "panicking_recovery_task";
+    }
+
+    #[derive(Clone)]
+    pub struct SuccessRecoveryTask;
+
+    #[async_trait(?Send)]
+    impl RecurringAsyncTaskNonSend for SuccessRecoveryTask {
+        async fn execute(self) -> (Duration, Self) {
+            SUCCESS_TASK_COUNTER.with(|c| c.set(c.get() + 1));
+
+            ic_cdk::call::Call::unbounded_wait(ic_cdk::api::canister_self(), "__self_call")
+                .await
+                .unwrap();
+
+            (Duration::from_secs(SUCCESS_TASK_DELAY_SECS), self)
+        }
+
+        fn initial_delay(&self) -> Duration {
+            Duration::from_secs(0)
+        }
+
+        fn recovery_delay(&self) -> Duration {
+            Duration::from_secs(RECOVERY_DELAY_SECS)
+        }
+
+        const NAME: &'static str = "success_recovery_task";
+    }
+}
```

### rs/node_rewards/canister/tests/recovery_timer_test.rs
```diff
@@ -0,0 +1,69 @@
+use candid::{Decode, Encode};
+use ic_nns_test_utils::common::build_node_rewards_test_wasm;
+use pocket_ic::PocketIcBuilder;
+use std::time::Duration;
+
+/// Starts both a successful and a panicking `RecurringAsyncTaskNonSend`, then
+/// verifies that:
+///   - the successful task keeps rescheduling itself through normal execution, and
+///   - the panicking task keeps being rescheduled via the recovery timer.
+#[tokio::test]
+async fn test_recovery_timer_rescheduling() {
+    let pocket_ic = PocketIcBuilder::new().with_nns_subnet().build_async().await;
+
+    let canister_id = pocket_ic.create_canister().await;
+    pocket_ic.add_cycles(canister_id, 100_000_000_000_000).await;
+    pocket_ic
+        .install_canister(
+            canister_id,
+            build_node_rewards_test_wasm().bytes(),
+            Encode!().unwrap(),
+            None,
+        )
+        .await;
+
+    pocket_ic
+        .update_call(
+            canister_id,
+            candid::Principal::anonymous(),
+            "start_recovery_test_tasks",
+            Encode!().unwrap(),
+        )
+        .await
+        .expect("Failed to start recovery test tasks");
+
+    // Advance time enough for many cycles. The successful task reschedules
+    // every 5s; the panicking task's recovery timer fires every 10s.
+    for _ in 0..30 {
+        pocket_ic.advance_time(Duration::from_secs(10)).await;
+        pocket_ic.tick().await;
+        pocket_ic.tick().await;
+    }
+
+    let response = pocket_ic
+        .query_call(
+            canister_id,
+            candid::Principal::anonymous(),
+            "get_recovery_test_counters",
+            Encode!().unwrap(),
+        )
+        .await
+        .expect("Failed to query counters");
+
+    let (success_counter, panic_counter) = Decode!(&response, u64, u64).unwrap();
+
+    // The successful task reschedules itself every 5s via normal execution,
+    // so over 300s it should have run many times.
+    assert!(
+        success_counter >= 10,
+        "Expected successful task to re-execute many times, but counter was {success_counter}"
+    );
+
+    // Without the recovery timer the panic counter would be exactly 1 (the
+    // first execution increments before the await/trap, then the task dies).
+    // With recovery it must be > 1.
+    assert!(
+        panic_counter > 1,
+        "Expected panicking task to be re-executed after recovery, but counter was {panic_counter}"
+    );
+}
```
