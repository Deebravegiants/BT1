# [?] fix overflow in `balance_to_point` conversion (#2706)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2023-12-22
Source: https://github.com/paritytech/polkadot-sdk/commit/4c0e0e071355c1048d75fba538c96c35ac743547
Type: security-commit

## Details
fix overflow in `balance_to_point` conversion (#2706)

Closes #416

As I mentioned in the above issue `balance_to_points` conversion
currently overflows the `Balance` types even before computing the actual
points for the given tokens. This fixes that,

## Patch
### substrate/frame/nomination-pools/src/lib.rs
```diff
@@ -2955,9 +2955,12 @@ impl<T: Config> Pallet<T> {
 			},
 			(false, false) => {
 				// Equivalent to (current_points / current_balance) * new_funds
-				balance(u256(current_points).saturating_mul(u256(new_funds)))
-					// We check for zero above
-					.div(current_balance)
+				balance(
+					u256(current_points)
+						.saturating_mul(u256(new_funds))
+						// We check for zero above
+						.div(u256(current_balance)),
+				)
 			},
 		}
 	}
```

### substrate/frame/nomination-pools/src/tests.rs
```diff
@@ -292,6 +292,28 @@ mod bonded_pool {
 			assert_ok!(pool.ok_to_join());
 		});
 	}
+
+	#[test]
+	fn points_and_balance_conversions_are_safe() {
+		ExtBuilder::default().build_and_execute(|| {
+			let bonded_pool = BondedPool::<Runtime> {
+				id: 123123,
+				inner: BondedPoolInner {
+					commission: Commission::default(),
+					member_counter: 1,
+					points: u128::MAX,
+					roles: DEFAULT_ROLES,
+					state: PoolState::Open,
+				},
+			};
+			StakingMock::set_bonded_balance(bonded_pool.bonded_account(), u128::MAX);
+
+			// Max out the points and balance of the pool and make sure the conversion works as
+			// expected and does not overflow.
+			assert_eq!(bonded_pool.balance_to_point(u128::MAX), u128::MAX);
+			assert_eq!(bonded_pool.points_to_balance(u128::MAX), u128::MAX);
+		})
+	}
 }
 
 mod reward_pool {
```
