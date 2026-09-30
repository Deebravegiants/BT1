# [?] Fix race condition between election creation and vote_cache triggering (#4610)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2024-05-09
Source: https://github.com/nanocurrency/nano-node/commit/9cd662cc702ded070395f0c9610c75414bcbcaeb
Type: security-commit

## Details
Fix race condition between election creation and vote_cache triggering (#4610)

The vote_cache is triggered after an election is created, and specifically after the active_elections mutex is released, which causes a race condition when checking the votes in an election.

## Patch
### nano/core_test/active_elections.cpp
```diff
@@ -436,7 +436,7 @@ TEST (inactive_votes_cache, multiple_votes)
 	node.scheduler.priority.activate (node.ledger.tx_begin_read (), nano::dev::genesis_key.pub);
 	std::shared_ptr<nano::election> election;
 	ASSERT_TIMELY (5s, election = node.active.election (send1->qualified_root ()));
-	ASSERT_EQ (3, election->votes ().size ()); // 2 votes and 1 default not_an_acount
+	ASSERT_TIMELY_EQ (5s, 3, election->votes ().size ()); // 2 votes and 1 default not_an_acount
 	ASSERT_EQ (2, node.stats.count (nano::stat::type::election, nano::stat::detail::vote_cached));
 }
 
```
