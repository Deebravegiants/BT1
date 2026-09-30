# [?] Fixing 3-cycle possible deadlock active_transactions -> election -> mdb_write_mutex. This was introduced with final votes and is alliviated by releasi

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2021-05-10
Source: https://github.com/nanocurrency/nano-node/commit/186babe0b0caa658facc0eb092642fcabc349b41
Type: security-commit

## Details
Fixing 3-cycle possible deadlock active_transactions -> election -> mdb_write_mutex. This was introduced with final votes and is alliviated by releasing the election mutex before issuing a final vote which requires the database write mutex. (#3269)

## Patch
### nano/node/election.cpp
```diff
@@ -293,7 +293,10 @@ void nano::election::confirm_if_quorum (nano::unique_lock<nano::mutex> & lock_a)
 	{
 		if (node.ledger.cache.final_votes_confirmation_canary.load () && !is_quorum.exchange (true) && node.config.enable_voting && node.wallets.reps ().voting > 0)
 		{
-			node.active.final_generator.add (root, status.winner->hash ());
+			auto hash = status.winner->hash ();
+			lock_a.unlock ();
+			node.active.final_generator.add (root, hash);
+			lock_a.lock ();
 		}
 		if (!node.ledger.cache.final_votes_confirmation_canary.load () || final_weight >= node.online_reps.delta ())
 		{
@@ -507,10 +510,13 @@ void nano::election::generate_votes () const
 {
 	if (node.config.enable_voting && node.wallets.reps ().voting > 0)
 	{
-		nano::lock_guard<nano::mutex> guard (mutex);
+		nano::unique_lock<nano::mutex> lock (mutex);
 		if (confirmed () || have_quorum (tally_impl ()))
 		{
-			node.active.final_generator.add (root, status.winner->hash ());
+			auto hash = status.winner->hash ();
+			lock.unlock ();
+			node.active.final_generator.add (root, hash);
+			lock.lock ();
 		}
 		else
 		{
```
