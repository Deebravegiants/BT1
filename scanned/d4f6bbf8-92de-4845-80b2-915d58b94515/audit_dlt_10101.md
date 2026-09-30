# [?] Avoiding tx -> gap_cache::mutex with gap_cache::mutex -> tx deadlock when resizing environment.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-07-03
Source: https://github.com/nanocurrency/nano-node/commit/a64125096584fb4095a3b9683088f613ee802871
Type: security-commit

## Details
Avoiding tx -> gap_cache::mutex with gap_cache::mutex -> tx deadlock when resizing environment.

## Patch
### rai/node/node.cpp
```diff
@@ -1268,13 +1268,13 @@ void rai::gap_cache::add (MDB_txn * transaction_a, rai::block const & block_a)
 
 void rai::gap_cache::vote (rai::vote const & vote_a)
 {
+	rai::transaction transaction (node.store.environment, nullptr, false);
 	std::lock_guard <std::mutex> lock (mutex);
 	auto hash (vote_a.block->hash ());
 	auto existing (blocks.get <1> ().find (hash));
 	if (existing != blocks.get <1> ().end ())
 	{
 		existing->votes->vote (vote_a);
-		rai::transaction transaction (node.store.environment, nullptr, false);
 		auto winner (node.ledger.winner (transaction, *existing->votes));
 		if (winner.first > bootstrap_threshold (transaction))
 		{
@@ -1410,6 +1410,8 @@ void rai::node::process_receive_many (rai::block const & block_a, std::function
 			}
 			++count;
 		}
+		// Let other threads get an opportunity to transaction lock
+		std::this_thread::yield ();
     }
 }
 
```
