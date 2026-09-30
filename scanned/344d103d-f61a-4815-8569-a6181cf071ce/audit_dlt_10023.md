# [?] fix: race condition in increment.

## Summary
Severity: Unknown
Chain: Movement
Component: movement-network/movement
Published: 2024-11-13
Source: https://github.com/movement-network/movement/commit/17d6e22e167f216eb27cccddbb6b02895bec0795
Type: security-commit

## Details
fix: race condition in increment.

## Patch
### util/collections/src/garbage/atomic/counted.rs
```diff
@@ -61,15 +61,36 @@ impl GcCounter {
 		let slot = slot_timestamp % self.num_slots;
 		let (active_slot_timestamp, count) = &self.value_lifetimes[slot as usize];
 
-		// Atomically check and set the timestamp if it doesn't match current_time
+		// Atomically check and set the timestamp if it doesn't match the current slot
 		let active_slot = active_slot_timestamp.load(Ordering::Relaxed);
+		let active_amount = count.load(Ordering::Relaxed);
+
 		if active_slot == slot {
-			// Same timestamp, increment count
+			// Same timestamp, increment count.
+			// At worst, this adds to a later slot.
+			// But, such should not happen under safe usage of this API.
+			// Unless gc windows are very small.
 			count.fetch_add(amount, Ordering::SeqCst);
 		} else {
-			// Different timestamp, reset slot for new period
-			active_slot_timestamp.store(slot_timestamp, Ordering::SeqCst);
-			count.store(amount, Ordering::SeqCst);
+			// now we will zero out the slot and add the new value
+			// Use compare_exchange to safely reset the slot and count only
+			if active_slot_timestamp
+				.compare_exchange(active_slot, slot_timestamp, Ordering::SeqCst, Ordering::Relaxed)
+				.is_ok()
+			{
+				// Successfully updated the timestamp, now set the count only if the active_amount is unchanged (no one trying to push to the slot)
+				// This creates a condition wherein someone will win the race to set the first value and then everyone else will just add to it
+				if !count
+					.compare_exchange(active_amount, amount, Ordering::SeqCst, Ordering::Relaxed)
+					.is_ok()
+				{
+					// otherwise fetch add
+					count.fetch_add(amount, Ordering::SeqCst);
+				}
+			} else {
+				// If another thread updated the timestamp, the amount will also have been reset, so just go ahead and add
+				count.fetch_add(amount, Ordering::SeqCst);
+			}
 		}
 	}
 
```
