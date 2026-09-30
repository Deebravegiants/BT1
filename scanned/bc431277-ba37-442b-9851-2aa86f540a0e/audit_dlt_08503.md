# [?] Avoid multisig reentrancy (#6445)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2020-06-19
Source: https://github.com/paritytech/substrate/commit/9cbda1eab93a1384086b4b88b6995669ed6435d2
Type: security-commit

## Details
Avoid multisig reentrancy (#6445)

## Patch
### frame/multisig/src/lib.rs
```diff
@@ -553,10 +553,13 @@ impl<T: Trait> Module<T> {
 				// verify weight
 				ensure!(call.get_dispatch_info().weight <= max_weight, Error::<T>::WeightTooLow);
 
-				let result = call.dispatch(RawOrigin::Signed(id.clone()).into());
-				T::Currency::unreserve(&m.depositor, m.deposit);
+				// Clean up storage before executing call to avoid an possibility of reentrancy
+				// attack.
 				<Multisigs<T>>::remove(&id, call_hash);
 				Self::clear_call(&call_hash);
+				T::Currency::unreserve(&m.depositor, m.deposit);
+
+				let result = call.dispatch(RawOrigin::Signed(id.clone()).into());
 				Self::deposit_event(RawEvent::MultisigExecuted(
 					who, timepoint, id, call_hash, result.map(|_| ()).map_err(|e| e.error)
 				));
```
