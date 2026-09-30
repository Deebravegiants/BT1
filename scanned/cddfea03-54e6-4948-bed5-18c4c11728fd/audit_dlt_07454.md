# [?] Fix deadlock in `chanmon_consistency` fuzzer

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2024-12-17
Source: https://github.com/lightningdevkit/rust-lightning/commit/351d41445736924d7c77000297722acacd183df3
Type: security-commit

## Details
Fix deadlock in `chanmon_consistency` fuzzer

bcaba29f9209071c4dd6932e7a1d7f2786eb1e99 introduced a deadlock in
the `chanmon_consistency` fuzzer by holding a lock on the route
expectations before sending a payment, which ultimately tries to
lock the route expectations. Here we fix this deadlock.

## Patch
### fuzz/src/chanmon_consistency.rs
```diff
@@ -552,8 +552,7 @@ fn send_payment(
 		.find(|chan| chan.short_channel_id == Some(dest_chan_id))
 		.map(|chan| (chan.next_outbound_htlc_minimum_msat, chan.next_outbound_htlc_limit_msat))
 		.unwrap_or((0, 0));
-	let mut next_routes = source.router.next_routes.lock().unwrap();
-	next_routes.push_back(Route {
+	source.router.next_routes.lock().unwrap().push_back(Route {
 		paths: vec![Path {
 			hops: vec![RouteHop {
 				pubkey: dest.get_our_node_id(),
@@ -623,8 +622,7 @@ fn send_hop_payment(
 		.map(|chan| (chan.next_outbound_htlc_minimum_msat, chan.next_outbound_htlc_limit_msat))
 		.unwrap_or((0, 0));
 	let first_hop_fee = 50_000;
-	let mut next_routes = source.router.next_routes.lock().unwrap();
-	next_routes.push_back(Route {
+	source.router.next_routes.lock().unwrap().push_back(Route {
 		paths: vec![Path {
 			hops: vec![
 				RouteHop {
```
