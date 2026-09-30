# [?] Fix race condition in `wallets::ongoing_compute_reps` (#4996)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-01-21
Source: https://github.com/nanocurrency/nano-node/commit/364c09894f272ca5933bc90524471a3e4a8dd5c6
Type: security-commit

## Details
Fix race condition in `wallets::ongoing_compute_reps` (#4996)

## Patch
### nano/core_test/wallets.cpp
```diff
@@ -24,6 +24,7 @@ TEST (wallets, open_create)
 {
 	nano::test::system system (1);
 	auto & node = *system.nodes[0];
+	node.wallets.stop (); // Stop node wallets to avoid race condition with local wallets sharing same LMDB environment
 	auto wallets = make_wallets (node);
 	ASSERT_EQ (1, wallets.items.size ()); // it starts out with a default wallet
 	auto id = nano::random_wallet_id ();
@@ -37,6 +38,7 @@ TEST (wallets, open_existing)
 {
 	nano::test::system system (1);
 	auto & node = *system.nodes[0];
+	node.wallets.stop (); // Stop node wallets to avoid race condition with local wallets sharing same LMDB environment
 	auto id (nano::random_wallet_id ());
 	{
 		auto wallets = make_wallets (node);
@@ -64,6 +66,7 @@ TEST (wallets, remove)
 {
 	nano::test::system system (1);
 	auto & node = *system.nodes[0];
+	node.wallets.stop (); // Stop node wallets to avoid race condition with local wallets sharing same LMDB environment
 	nano::wallet_id one (1);
 	{
 		auto wallets = make_wallets (node);
```

### nano/node/wallet.cpp
```diff
@@ -1825,11 +1825,10 @@ void nano::wallets::compute_reps ()
 void nano::wallets::ongoing_compute_reps ()
 {
 	compute_reps ();
-	auto & node_l (node);
 	// Representation drifts quickly on the test network but very slowly on the live network
 	auto compute_delay = network_params.network.is_dev_network () ? std::chrono::milliseconds (10) : (network_params.network.is_test_network () ? std::chrono::milliseconds (nano::test_scan_wallet_reps_delay ()) : std::chrono::minutes (15));
-	workers.post_delayed (compute_delay, [&node_l] () {
-		node_l.wallets.ongoing_compute_reps ();
+	workers.post_delayed (compute_delay, [this] () {
+		ongoing_compute_reps ();
 	});
 }
 
```
