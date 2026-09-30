# [?] Fix dust buffer feerate calculation overflow

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2023-12-24
Source: https://github.com/lightningdevkit/rust-lightning/commit/3b6a361ae76a087ac10c2e59f9163188fd5c20e1
Type: security-commit

## Details
Fix dust buffer feerate calculation overflow

If a peer provides a feerate which nears `u32::MAX`, we may
overflow calculating the dust buffer feerate, leading to spuriously
keeping non-anchor channels open when they should be force-closed.

## Patch
### lightning/src/ln/channel.rs
```diff
@@ -1872,7 +1872,8 @@ impl<SP: Deref> ChannelContext<SP> where SP::Target: SignerProvider  {
 		if let Some(feerate) = outbound_feerate_update {
 			feerate_per_kw = cmp::max(feerate_per_kw, feerate);
 		}
-		cmp::max(2530, feerate_per_kw * 1250 / 1000)
+		let feerate_plus_quarter = feerate_per_kw.checked_mul(1250).map(|v| v / 1000);
+		cmp::max(2530, feerate_plus_quarter.unwrap_or(u32::max_value()))
 	}
 
 	/// Get forwarding information for the counterparty.
```
