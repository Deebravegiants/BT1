# [?] fix(orbiters): panic if we trying to add an orbiter just after removing another (#1527)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2022-05-20
Source: https://github.com/moonbeam-foundation/moonbeam/commit/7a6f4bd158361173d76aabe99111a293182ac557
Type: security-commit

## Details
fix(orbiters): panic if we trying to add an orbiter just after removing another (#1527)

* test to reproduce the orbiter bug

* ensure that next_orbiter <= orbiters.len()

## Patch
### pallets/moonbeam-orbiters/src/tests.rs
```diff
@@ -180,6 +180,45 @@ fn test_collator_remove_orbiter() {
 		});
 }
 
+#[test]
+fn test_collator_remove_orbiter_then_add_orbiter() {
+	ExtBuilder::default()
+		.with_balances(vec![(2, 20_000), (3, 20_000)])
+		.with_min_orbiter_deposit(10_000)
+		.build()
+		.execute_with(|| {
+			// Add a collator to the orbiter program
+			assert_ok!(MoonbeamOrbiters::add_collator(Origin::root(), 1),);
+			// Register an orbiter
+			assert_ok!(MoonbeamOrbiters::orbiter_register(Origin::signed(2)),);
+			assert_ok!(MoonbeamOrbiters::collator_add_orbiter(Origin::signed(1), 2),);
+
+			// Try to remove an orbiter to a collator pool, should success
+			assert_ok!(MoonbeamOrbiters::collator_remove_orbiter(
+				Origin::signed(1),
+				2
+			),);
+			System::assert_last_event(
+				Event::<Test>::OrbiterLeaveCollatorPool {
+					collator: 1,
+					orbiter: 2,
+				}
+				.into(),
+			);
+
+			// Try to register another orbiter, should success
+			assert_ok!(MoonbeamOrbiters::orbiter_register(Origin::signed(3)),);
+			assert_ok!(MoonbeamOrbiters::collator_add_orbiter(Origin::signed(1), 3),);
+			System::assert_last_event(
+				Event::<Test>::OrbiterJoinCollatorPool {
+					collator: 1,
+					orbiter: 3,
+				}
+				.into(),
+			);
+		});
+}
+
 #[test]
 fn test_orbiter_register_fail_if_insufficient_balance() {
 	ExtBuilder::default()
```

### pallets/moonbeam-orbiters/src/types.rs
```diff
@@ -66,6 +66,9 @@ impl<AccountId> Default for CollatorPoolInfo<AccountId> {
 
 impl<AccountId: Clone + PartialEq> CollatorPoolInfo<AccountId> {
 	pub(super) fn add_orbiter(&mut self, orbiter: AccountId) {
+		if self.next_orbiter > self.orbiters.len() as u32 {
+			self.next_orbiter = 0;
+		}
 		self.orbiters.insert(self.next_orbiter as usize, orbiter);
 		self.next_orbiter += 1;
 	}
```
