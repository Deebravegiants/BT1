# [?] Fixing deadlock between db transaction and active_transactions lock.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-03-14
Source: https://github.com/nanocurrency/nano-node/commit/81ad6bd0c0147ce11fa0653e4b52587094b97e8a
Type: security-commit

## Details
Fixing deadlock between db transaction and active_transactions lock.

## Patch
### rai/node/node.cpp
```diff
@@ -2470,10 +2470,10 @@ void rai::election::vote (rai::vote const & vote_a)
 void rai::active_transactions::announce_votes ()
 {
 	std::vector <rai::block_hash> inactive;
+	rai::transaction transaction (node.store.environment, nullptr, true);
 	std::lock_guard <std::mutex> lock (mutex);
 	size_t announcements (0);
 	{
-		rai::transaction transaction (node.store.environment, nullptr, true);
 		auto i (roots.begin ());
 		auto n (roots.end ());
 		// Announce our decision for up to `announcements_per_interval' conflicts
```
