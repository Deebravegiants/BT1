# [?] rosetta: fix historical vesting liquid/locked balance underflow

## Summary
Severity: Unknown
Chain: Mina
Component: MinaProtocol/mina
Published: 2026-07-20
Source: https://github.com/MinaProtocol/mina/commit/a26652a650ab6b6f20e1a0370fb874c8ac0dbcbe
Type: security-commit

## Details
rosetta: fix historical vesting liquid/locked balance underflow

Compute the liquid balance directly as total - min_balance(end_slot) instead
of total + incremental_balance_between_slots. The old base was the *total*
balance rather than the liquid base (total - min_balance(start_slot)), so for
accounts with an active vesting schedule the reported liquid_balance exceeded
the total and drove the downstream unsigned `locked = total - liquid` into a
2^64 wraparound.

This is a pure behavior fix: liquid_balance_at_slot drops the now-unused
~start_slot parameter (the corrected formula only depends on end_slot), and
the regression tests from the previous commit are updated only to match that
dropped parameter -- their assertions and expected values are unchanged, and
all now turn green.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

## Patch
### src/app/rosetta/lib/account.ml
```diff
@@ -142,9 +142,10 @@ module Sql = struct
           , timing_id ) )
   end
 
-  let compute_incremental_balance
-      (timing_info : Archive_lib.Processor.Timing_info.t) ~start_slot ~end_slot
-      =
+  (* The account's minimum (locked) balance at [global_slot], per its vesting
+     schedule. [Mina_base.Account.min_balance_at_slot] clamps at zero. *)
+  let min_balance_at_slot (timing_info : Archive_lib.Processor.Timing_info.t)
+      ~global_slot : Unsigned.UInt64.t =
     let cliff_time =
       Mina_numbers.Global_slot_since_genesis.of_int
         (Int.of_int64_exn timing_info.cliff_time)
@@ -160,28 +161,33 @@ module Sql = struct
     let initial_minimum_balance =
       MinaCurrency.Balance.of_string timing_info.initial_minimum_balance
     in
-    Mina_base.Account.incremental_balance_between_slots ~start_slot ~end_slot
-      ~cliff_time ~cliff_amount ~vesting_period ~vesting_increment
-      ~initial_minimum_balance
+    Mina_base.Account.min_balance_at_slot ~global_slot ~cliff_time ~cliff_amount
+      ~vesting_period ~vesting_increment ~initial_minimum_balance
+    |> MinaCurrency.Balance.to_amount |> MinaCurrency.Amount.to_uint64
 
   (* Pure computation of an account's liquid (unlocked) balance at [end_slot],
      given its [total_balance] and (optional) vesting schedule. Extracted out
      of [find_current_balance] so it can be exercised directly by inline tests
      -- [find_current_balance] itself is only reachable behind a database
-     handle. Behaviour-preserving: still computes exactly what production did
-     before this extraction. *)
-  let liquid_balance_at_slot ~total_balance ~timing_info_opt ~start_slot
-      ~end_slot : Unsigned.UInt64.t =
+     handle.
+
+     The liquid balance is the total minus the portion still locked by the
+     vesting schedule at [end_slot]: liquid(end) = total - min_balance(end).
+     This replaces the previous (incorrect) formula, which added the
+     incremental unlocked amount to the *total* balance rather than to the
+     liquid base, and could drive the downstream unsigned
+     [locked = total - liquid] into a 2^64 wraparound. *)
+  let liquid_balance_at_slot ~total_balance ~timing_info_opt ~end_slot :
+      Unsigned.UInt64.t =
     match timing_info_opt with
     | None ->
         (* No vesting schedule: the whole balance is liquid. *)
         total_balance
     | Some timing_info ->
-        let incremental_balance_between_slots =
-          compute_incremental_balance timing_info ~start_slot ~end_slot
+        let min_balance =
+          min_balance_at_slot timing_info ~global_slot:end_slot
         in
-        Unsigned.UInt64.Infix.(
-          total_balance + incremental_balance_between_slots)
+        Unsigned.UInt64.sub total_balance min_balance
 
   let find_current_balance (module Conn : Mina_caqti.CONNECTION)
       ~requested_block_global_slot_since_genesis
@@ -201,18 +207,13 @@ module Sql = struct
       Mina_numbers.Global_slot_since_genesis.of_uint32
         (Unsigned.UInt32.of_int64 requested_block_global_slot_since_genesis)
     in
-    (* This block was in the genesis ledger and has been involved in at least
-       one user or internal command. We compute the change in its balance
-       between the most recent command and the start block (if it has vesting
-       it may have changed). *)
-    let start_slot =
-      Mina_numbers.Global_slot_since_genesis.of_int
-        (Int.of_int64_exn last_relevant_command.block_global_slot_since_genesis)
-    in
+    (* This block was in the genesis ledger and may have an active vesting
+       schedule, so the liquid portion of its (unchanged) total balance depends
+       on the requested slot. *)
     let liquid_balance =
       liquid_balance_at_slot
         ~total_balance:(UInt64.of_int64 last_relevant_command.total_balance)
-        ~timing_info_opt ~start_slot ~end_slot
+        ~timing_info_opt ~end_slot
       |> UInt64.to_int64
     in
     let nonce = UInt64.of_int64 last_relevant_command.nonce in
@@ -238,54 +239,49 @@ module Sql = struct
         }
 
       (* Fixture: an account whose entire balance is its initial minimum
-         balance (so liquid(start) = 0), observed partway through vesting.
+         balance, observed at various points in its vesting schedule.
 
            initial_minimum_balance = 100   total = 100
            cliff_time = 10   cliff_amount = 0
            vesting_period = 1   vesting_increment = 10
 
          At end_slot 12 -> 2 vesting periods past the cliff ->
            min_balance(12) = 100 - 2*10 = 80
-           liquid(12)      = total - min_balance(12) = 20     (correct)
-           locked(12)      = 80
-
-         The buggy production formula instead computes
-           liquid = total + incremental = 100 + (min(0) - min(12)) = 120,
-         which exceeds total and underflows locked = total - liquid. *)
+           liquid(12)      = total - min_balance(12) = 20
+           locked(12)      = 80 *)
       let total = uint64 100
 
       let timing_info =
         Some
           (timing ~initial_minimum_balance:100 ~cliff_time:10 ~cliff_amount:0
              ~vesting_period:1 ~vesting_increment:10 )
 
-      let liquid ~start ~end_ =
+      let liquid end_ =
         liquid_balance_at_slot ~total_balance:total ~timing_info_opt:timing_info
-          ~start_slot:(Slot.of_int start) ~end_slot:(Slot.of_int end_)
+          ~end_slot:(Slot.of_int end_)
 
       let%test "liquid never exceeds total (partially vested)" =
-        Unsigned.UInt64.compare (liquid ~start:0 ~end_:12) total <= 0
+        Unsigned.UInt64.compare (liquid 12) total <= 0
 
       let%test "locked never underflows (locked <= total)" =
-        let l = liquid ~start:0 ~end_:12 in
+        let l = liquid 12 in
         Unsigned.UInt64.compare (Unsigned.UInt64.sub total l) total <= 0
 
       let%test "liquid = total - min_balance(end_slot)" =
-        Unsigned.UInt64.equal (liquid ~start:0 ~end_:12) (uint64 20)
+        Unsigned.UInt64.equal (liquid 12) (uint64 20)
 
       let%test "pre-cliff: liquid = total - initial_minimum_balance" =
-        (* start and end both before the cliff: nothing has unlocked, so the
-           liquid balance is total minus the still-fully-locked min balance. *)
-        Unsigned.UInt64.equal (liquid ~start:0 ~end_:5) (uint64 0)
+        (* Before the cliff nothing has unlocked, so the liquid balance is
+           total minus the still-fully-locked min balance (here, zero). *)
+        Unsigned.UInt64.equal (liquid 5) (uint64 0)
 
       let%test "fully vested: liquid = total, locked = 0" =
-        let l = liquid ~start:0 ~end_:1000 in
-        Unsigned.UInt64.equal l total
+        Unsigned.UInt64.equal (liquid 1000) total
 
       let%test "untimed account is fully liquid" =
         Unsigned.UInt64.equal
           (liquid_balance_at_slot ~total_balance:total ~timing_info_opt:None
-             ~start_slot:(Slot.of_int 0) ~end_slot:(Slot.of_int 12) )
+             ~end_slot:(Slot.of_int 12) )
           total
     end )
 
```
