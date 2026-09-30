# [?] Fixing a race condition in active_transactions.fork_replacement_tally (#4385)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2024-01-22
Source: https://github.com/nanocurrency/nano-node/commit/06d8b4e7ba20af559e1175fc91b396c417608c71
Type: security-commit

## Details
Fixing a race condition in active_transactions.fork_replacement_tally (#4385)

I did not check the unit test, just fixing the race condition I see
because the CI failed on the assert where it couldn't find the election.
The election finding needs to be inside an ASSERT_TIMELY.

## Patch
### nano/core_test/active_transactions.cpp
```diff
@@ -898,11 +898,10 @@ TEST (active_transactions, fork_replacement_tally)
 					.build_shared ();
 		node1.process_active (fork);
 	}
-	ASSERT_TIMELY (5s, !node1.active.empty ());
 
 	// Check overflow of blocks
-	auto election = node1.active.election (send_last->qualified_root ());
-	ASSERT_NE (nullptr, election);
+	std::shared_ptr<nano::election> election;
+	ASSERT_TIMELY (5s, election = node1.active.election (send_last->qualified_root ()));
 	ASSERT_TIMELY_EQ (5s, max_blocks, election->blocks ().size ());
 
 	// Generate forks with votes to prevent new block insertion to election
```
