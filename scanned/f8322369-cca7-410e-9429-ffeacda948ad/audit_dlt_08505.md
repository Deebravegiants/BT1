# [?] babe: fix overflow in check_equivocation (#5818)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2020-04-28
Source: https://github.com/paritytech/substrate/commit/207902d5f131d03e950251ecabc37c38745cd7db
Type: security-commit

## Details
babe: fix overflow in check_equivocation (#5818)

## Patch
### client/consensus/slots/src/aux_schema.rs
```diff
@@ -85,8 +85,8 @@ pub fn check_equivocation<C, H, P>(
 		P: Clone + Encode + Decode + PartialEq,
 {
 	// We don't check equivocations for old headers out of our capacity.
-	if slot_now - slot > MAX_SLOT_CAPACITY {
-		return Ok(None)
+	if slot_now.saturating_sub(slot) > MAX_SLOT_CAPACITY {
+		return Ok(None);
 	}
 
 	// Key for this slot.
@@ -102,6 +102,11 @@ pub fn check_equivocation<C, H, P>(
 	let first_saved_slot = load_decode::<_, u64>(backend, &slot_header_start[..])?
 		.unwrap_or(slot);
 
+	if slot_now < first_saved_slot {
+		// The code below assumes that slots will be visited sequentially.
+		return Ok(None);
+	}
+
 	for (prev_header, prev_signer) in headers_with_sig.iter() {
 		// A proof of equivocation consists of two headers:
 		// 1) signed by the same voter,
@@ -114,7 +119,7 @@ pub fn check_equivocation<C, H, P>(
 					snd_header: header.clone(),
 				}));
 			} else {
-				//  We don't need to continue in case of duplicated header,
+				// We don't need to continue in case of duplicated header,
 				// since it's already saved and a possible equivocation
 				// would have been detected before.
 				return Ok(None)
```
