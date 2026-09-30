# [?] fix: late messages are no longer crashing a timed-out ceremony (#2535) (#2629)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2022-12-16
Source: https://github.com/chainflip-io/chainflip-backend/commit/817035a5cc2517f5c4683f377c021e4c1637aa75
Type: security-commit

## Details
fix: late messages are no longer crashing a timed-out ceremony (#2535) (#2629)

* fix: late messages are no longer crashing a timed-out ceremony (#2535)

* chore: addrss review comments

## Patch
### engine/src/multisig/client/ceremony_manager.rs
```diff
@@ -587,7 +587,12 @@ impl<Ceremony: CeremonyTrait> CeremonyStates<Ceremony> {
 			hash_map::Entry::Occupied(entry) => entry.into_mut(),
 		};
 
-		ceremony_handle.message_sender.send((sender_id, data)).unwrap();
+		// NOTE: There is a short delay between dropping the ceremony runner (and any channels
+		// associated with it) and dropping the corresponding ceremony handle, which makes it
+		// possible for the following `send` to fail
+		if ceremony_handle.message_sender.send((sender_id, data)).is_err() {
+			slog::debug!(logger, "Ignoring data: ceremony runner has been dropped");
+		}
 	}
 
 	/// Returns the state for the given ceremony id if it exists,
```

### engine/src/multisig/client/keygen/keygen_stages.rs
```diff
@@ -160,11 +160,17 @@ impl<Crypto: CryptoScheme> BroadcastStageProcessor<KeygenCeremony<Crypto>>
 	) -> StageResult<KeygenCeremony<Crypto>> {
 		let hash_commitments = match verify_broadcasts(messages, &self.common.logger) {
 			Ok(hash_commitments) => hash_commitments,
-			Err((reported_parties, abort_reason)) =>
+			Err((reported_parties, abort_reason)) => {
+				slog::warn!(
+					self.common.logger,
+					"Broadcast verification is not successful for {}",
+					Self::NAME
+				);
 				return KeygenStageResult::Error(
 					reported_parties,
 					KeygenFailureReason::BroadcastFailure(abort_reason, Self::NAME),
-				),
+				)
+			},
 		};
 
 		slog::debug!(self.common.logger, "{} is successful", Self::NAME);
```
