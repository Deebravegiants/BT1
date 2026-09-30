# [?] Use SignedAmount::unsigned_abs to avoid overflow

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-02-04
Source: https://github.com/lightningdevkit/rust-lightning/commit/2d948fdd33bd3f509fae90f588b27c040a15d7aa
Type: security-commit

## Details
Use SignedAmount::unsigned_abs to avoid overflow

In debug mode, using SignedAmount::abs can lead to an integer overflow
when used with SignedAmount::MIN. Use SignedAmount::unsigned_abs to
avoid this.

## Patch
### lightning/src/ln/channel.rs
```diff
@@ -2664,8 +2664,8 @@ impl FundingScope {
 		their_funding_contribution: SignedAmount, counterparty_funding_pubkey: PublicKey,
 		our_new_holder_keys: ChannelPublicKeys,
 	) -> Self {
-		debug_assert!(our_funding_contribution.abs() <= SignedAmount::MAX_MONEY);
-		debug_assert!(their_funding_contribution.abs() <= SignedAmount::MAX_MONEY);
+		debug_assert!(our_funding_contribution.unsigned_abs() <= Amount::MAX_MONEY);
+		debug_assert!(their_funding_contribution.unsigned_abs() <= Amount::MAX_MONEY);
 
 		let post_channel_value = prev_funding.compute_post_splice_value(
 			our_funding_contribution.to_sat(),
@@ -12155,15 +12155,15 @@ where
 	fn validate_splice_contributions(
 		&self, our_funding_contribution: SignedAmount, their_funding_contribution: SignedAmount,
 	) -> Result<(), String> {
-		if our_funding_contribution.abs() > SignedAmount::MAX_MONEY {
+		if our_funding_contribution.unsigned_abs() > Amount::MAX_MONEY {
 			return Err(format!(
 				"Channel {} cannot be spliced; our {} contribution exceeds the total bitcoin supply",
 				self.context.channel_id(),
 				our_funding_contribution,
 			));
 		}
 
-		if their_funding_contribution.abs() > SignedAmount::MAX_MONEY {
+		if their_funding_contribution.unsigned_abs() > Amount::MAX_MONEY {
 			return Err(format!(
 				"Channel {} cannot be spliced; their {} contribution exceeds the total bitcoin supply",
 				self.context.channel_id(),
```
