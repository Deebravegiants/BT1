# [?] [fix] Identify dummy-hop relay underflow

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-03-12
Source: https://github.com/lightningdevkit/rust-lightning/commit/b79652e63037d45b331c8f5bc91ee42c40fd00bd
Type: security-commit

## Details
[fix] Identify dummy-hop relay underflow

Dummy hops reuse blinded forwarding validation, but an amount or CLTV
underflow at this stage occurs while processing a locally peeled dummy hop.
Report that context instead of describing the failure as a generic blinded
forward so logs identify the failing layer accurately.

## Patch
### lightning/src/ln/onion_payment.rs
```diff
@@ -690,7 +690,7 @@ pub(super) fn decode_incoming_update_add_htlc_onion<NS: NodeSigner, L: Logger, T
 			) {
 				Ok((amt, cltv)) => (amt, cltv),
 				Err(()) => {
-					return encode_relay_error("Underflow calculating outbound amount or cltv value for blinded forward",
+					return encode_relay_error("Underflow calculating outbound amount or cltv value for dummy hop",
 						LocalHTLCFailureReason::InvalidOnionBlinding, shared_secret.secret_bytes(), None, &[0; 32]);
 				}
 			};
```
