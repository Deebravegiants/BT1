# [?] Fix potential cases where max_dust_htlc_exposure_msat overflows

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2023-11-09
Source: https://github.com/lightningdevkit/rust-lightning/commit/55da9c434eeb6f108463e1c8d78914c759f43999
Type: security-commit

## Details
Fix potential cases where max_dust_htlc_exposure_msat overflows

## Patch
### lightning/src/ln/channel.rs
```diff
@@ -48,6 +48,7 @@ use crate::util::scid_utils::scid_from_parts;
 use crate::io;
 use crate::prelude::*;
 use core::{cmp,mem,fmt};
+use core::convert::TryInto;
 use core::ops::Deref;
 #[cfg(any(test, fuzzing, debug_assertions))]
 use crate::sync::Mutex;
@@ -1168,8 +1169,8 @@ impl<SP: Deref> ChannelContext<SP> where SP::Target: SignerProvider  {
 		match self.config.options.max_dust_htlc_exposure {
 			MaxDustHTLCExposure::FeeRateMultiplier(multiplier) => {
 				let feerate_per_kw = fee_estimator.bounded_sat_per_1000_weight(
-					ConfirmationTarget::OnChainSweep);
-				feerate_per_kw as u64 * multiplier
+					ConfirmationTarget::OnChainSweep) as u64;
+				feerate_per_kw.saturating_mul(multiplier)
 			},
 			MaxDustHTLCExposure::FixedLimitMsat(limit) => limit,
 		}
@@ -1753,14 +1754,14 @@ impl<SP: Deref> ChannelContext<SP> where SP::Target: SignerProvider  {
 			 context.holder_dust_limit_satoshis       + dust_buffer_feerate * htlc_timeout_tx_weight(context.get_channel_type()) / 1000)
 		};
 		let on_counterparty_dust_htlc_exposure_msat = inbound_stats.on_counterparty_tx_dust_exposure_msat + outbound_stats.on_counterparty_tx_dust_exposure_msat;
-		if on_counterparty_dust_htlc_exposure_msat as i64 + htlc_success_dust_limit as i64 * 1000 - 1 > max_dust_htlc_exposure_msat as i64 {
+		if on_counterparty_dust_htlc_exposure_msat as i64 + htlc_success_dust_limit as i64 * 1000 - 1 > max_dust_htlc_exposure_msat.try_into().unwrap_or(i64::max_value()) {
 			remaining_msat_below_dust_exposure_limit =
 				Some(max_dust_htlc_exposure_msat.saturating_sub(on_counterparty_dust_htlc_exposure_msat));
 			dust_exposure_dust_limit_msat = cmp::max(dust_exposure_dust_limit_msat, htlc_success_dust_limit * 1000);
 		}
 
 		let on_holder_dust_htlc_exposure_msat = inbound_stats.on_holder_tx_dust_exposure_msat + outbound_stats.on_holder_tx_dust_exposure_msat;
-		if on_holder_dust_htlc_exposure_msat as i64 + htlc_timeout_dust_limit as i64 * 1000 - 1 > max_dust_htlc_exposure_msat as i64 {
+		if on_holder_dust_htlc_exposure_msat as i64 + htlc_timeout_dust_limit as i64 * 1000 - 1 > max_dust_htlc_exposure_msat.try_into().unwrap_or(i64::max_value()) {
 			remaining_msat_below_dust_exposure_limit = Some(cmp::min(
 				remaining_msat_below_dust_exposure_limit.unwrap_or(u64::max_value()),
 				max_dust_htlc_exposure_msat.saturating_sub(on_holder_dust_htlc_exposure_msat)));
```
