# [?] Fixing race condition identified by TSAN when reading status.winner which is now directly read within election::confirmed as of https://github.com/nan

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2023-04-24
Source: https://github.com/nanocurrency/nano-node/commit/a3026afca1560d477d13fc5ebb1688dda999de38
Type: security-commit

## Details
Fixing race condition identified by TSAN when reading status.winner which is now directly read within election::confirmed as of https://github.com/nanocurrency/nano-node/pull/4200 (#4218)

## Patch
### nano/node/election.cpp
```diff
@@ -124,6 +124,11 @@ bool nano::election::state_change (nano::election::state_t expected_a, nano::ele
 	return result;
 }
 
+bool nano::election::confirmed (nano::unique_lock<nano::mutex> & lock) const
+{
+	return node.block_confirmed (status.winner->hash ());
+}
+
 std::chrono::milliseconds nano::election::confirm_req_time () const
 {
 	switch (behavior ())
@@ -158,7 +163,8 @@ void nano::election::transition_active ()
 
 bool nano::election::confirmed () const
 {
-	return node.block_confirmed (status.winner->hash ());
+	nano::unique_lock<nano::mutex> lock{ mutex };
+	return confirmed (lock);
 }
 
 bool nano::election::status_confirmed () const
@@ -188,7 +194,7 @@ void nano::election::broadcast_vote ()
 	nano::unique_lock<nano::mutex> lock{ mutex };
 	if (last_vote + std::chrono::milliseconds (node.config.network_params.network.vote_broadcast_interval) < std::chrono::steady_clock::now ())
 	{
-		broadcast_vote_impl ();
+		broadcast_vote_impl (lock);
 		last_vote = std::chrono::steady_clock::now ();
 	}
 }
@@ -436,7 +442,7 @@ nano::election_vote_result nano::election::vote (nano::account const & rep, uint
 
 	node.stats.inc (nano::stat::type::election, vote_source_a == vote_source::live ? nano::stat::detail::vote_new : nano::stat::detail::vote_cached);
 
-	if (!confirmed ())
+	if (!confirmed (lock))
 	{
 		confirm_if_quorum (lock);
 	}
@@ -448,7 +454,7 @@ bool nano::election::publish (std::shared_ptr<nano::block> const & block_a)
 	nano::unique_lock<nano::mutex> lock{ mutex };
 
 	// Do not insert new blocks if already confirmed
-	auto result (confirmed ());
+	auto result = confirmed (lock);
 	if (!result && last_blocks.size () >= max_blocks && last_blocks.find (block_a->hash ()) == last_blocks.end ())
 	{
 		if (!replace_by_weight (lock, block_a->hash ()))
@@ -501,15 +507,15 @@ std::shared_ptr<nano::block> nano::election::winner () const
 	return status.winner;
 }
 
-void nano::election::broadcast_vote_impl ()
+void nano::election::broadcast_vote_impl (nano::unique_lock<nano::mutex> & lock)
 {
 	debug_assert (!mutex.try_lock ());
 
 	if (node.config.enable_voting && node.wallets.reps ().voting > 0)
 	{
 		node.stats.inc (nano::stat::type::election, nano::stat::detail::generate_vote);
 
-		if (confirmed () || have_quorum (tally_impl ()))
+		if (confirmed (lock) || have_quorum (tally_impl ()))
 		{
 			node.stats.inc (nano::stat::type::election, nano::stat::detail::generate_vote_final);
 			node.final_generator.add (root, status.winner->hash ()); // Broadcasts vote to the network
```

### nano/node/election.hpp
```diff
@@ -110,6 +110,7 @@ class election final : public std::enable_shared_from_this<nano::election>
 
 	bool valid_change (nano::election::state_t, nano::election::state_t) const;
 	bool state_change (nano::election::state_t, nano::election::state_t);
+	bool confirmed (nano::unique_lock<nano::mutex> & lock) const;
 
 public: // State transitions
 	bool transition_time (nano::confirmation_solicitor &);
@@ -174,7 +175,7 @@ class election final : public std::enable_shared_from_this<nano::election>
 	 * Broadcast vote for current election winner. Generates final vote if reached quorum or already confirmed
 	 * Requires mutex lock
 	 */
-	void broadcast_vote_impl ();
+	void broadcast_vote_impl (nano::unique_lock<nano::mutex> & lock);
 	void remove_votes (nano::block_hash const &);
 	void remove_block (nano::block_hash const &);
 	bool replace_by_weight (nano::unique_lock<nano::mutex> & lock_a, nano::block_hash const &);
```
