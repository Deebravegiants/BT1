# [?] Fix deadlock for elections escalation (#1254)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-10-03
Source: https://github.com/nanocurrency/nano-node/commit/a9c113003ed99c25793d77791617c546e382aca6
Type: security-commit

## Details
Fix deadlock for elections escalation (#1254)

## Patch
### rai/node/node.cpp
```diff
@@ -3946,6 +3946,30 @@ void rai::active_transactions::announce_votes ()
 					auto tally_l (election_l->tally (transaction));
 					election_l->log_votes (tally_l);
 				}
+				/* Escalation for long unconfirmed elections
+				Start new elections for previous block & source
+				if there are less than 100 active elections */
+				if (i->announcements % announcement_long == 1 && roots.size () < 100)
+				{
+					auto previous_hash (election_l->status.winner->previous ());
+					if (!previous_hash.is_zero ())
+					{
+						auto previous (node.store.block_get (transaction, previous_hash));
+						if (previous != nullptr)
+						{
+							add (std::make_pair (std::move (previous), nullptr));
+						}
+					}
+					auto source_hash (node.ledger.block_source (transaction, *election_l->status.winner));
+					if (!source_hash.is_zero ())
+					{
+						auto source (node.store.block_get (transaction, source_hash));
+						if (source != nullptr)
+						{
+							add (std::make_pair (std::move (source), nullptr));
+						}
+					}
+				}
 			}
 			if (i->announcements < announcement_long || i->announcements % announcement_long == 1)
 			{
@@ -4097,10 +4121,15 @@ bool rai::active_transactions::start (std::shared_ptr<rai::block> block_a, std::
 }
 
 bool rai::active_transactions::start (std::pair<std::shared_ptr<rai::block>, std::shared_ptr<rai::block>> blocks_a, std::function<void(std::shared_ptr<rai::block>)> const & confirmation_action_a)
+{
+	std::lock_guard<std::mutex> lock (mutex);
+	return add (blocks_a, confirmation_action_a);
+}
+
+bool rai::active_transactions::add (std::pair<std::shared_ptr<rai::block>, std::shared_ptr<rai::block>> blocks_a, std::function<void(std::shared_ptr<rai::block>)> const & confirmation_action_a)
 {
 	assert (blocks_a.first != nullptr);
 	auto error (true);
-	std::lock_guard<std::mutex> lock (mutex);
 	if (!stopped)
 	{
 		auto primary_block (blocks_a.first);
```

### rai/node/node.hpp
```diff
@@ -101,6 +101,7 @@ class active_transactions
 	// Should only be used for old elections
 	// The first block should be the one in the ledger
 	bool start (std::pair<std::shared_ptr<rai::block>, std::shared_ptr<rai::block>>, std::function<void(std::shared_ptr<rai::block>)> const & = [](std::shared_ptr<rai::block>) {});
+	bool add (std::pair<std::shared_ptr<rai::block>, std::shared_ptr<rai::block>>, std::function<void(std::shared_ptr<rai::block>)> const & = [](std::shared_ptr<rai::block>) {});
 	// If this returns true, the vote is a replay
 	// If this returns false, the vote may or may not be a replay
 	bool vote (std::shared_ptr<rai::vote>);
```
