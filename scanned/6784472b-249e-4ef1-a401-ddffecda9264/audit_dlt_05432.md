# [?] Fix race condition in confirm_quorum test (#5096)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-06-30
Source: https://github.com/nanocurrency/nano-node/commit/d91fa07c42e47264f5b0fcc815db837858df0bb5
Type: security-commit

## Details
Fix race condition in confirm_quorum test (#5096)

node.confirm_quorum intermittently failed on slow/contended CI runners at
ASSERT_EQ (1, election->votes ().size ()) with a value of 2. Between
processing send1 and the send_action that drained genesis below quorum, the
backlog scheduler could activate send1's election while genesis was still a
heavy principal representative, letting genesis cast a sub-quorum vote that
was cached permanently. The election's confirmation outcome was never at
risk; only the vote-count assertion was racy.

Drain genesis to zero weight through the ledger directly and insert the
voting key only once that is done, so genesis can never vote on the election
while it still holds weight, regardless of scheduler timing.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### nano/core_test/node.cpp
```diff
@@ -1772,10 +1772,10 @@ TEST (node, confirm_quorum)
 {
 	nano::test::system system (1);
 	auto & node1 = *system.nodes[0];
-	system.wallet (0)->insert_adhoc (nano::dev::genesis_key.prv);
-	// Put greater than node.delta () in pending so quorum can't be reached
+	nano::state_block_builder builder;
+	// Move all genesis weight into pending so it drops below quorum and can never confirm an election
 	nano::amount new_balance = node1.online_reps.delta () - nano::Knano_ratio;
-	auto send1 = nano::state_block_builder ()
+	auto send1 = builder.make_block ()
 				 .account (nano::dev::genesis_key.pub)
 				 .previous (nano::dev::genesis->hash ())
 				 .representative (nano::dev::genesis_key.pub)
@@ -1785,10 +1785,22 @@ TEST (node, confirm_quorum)
 				 .work (*node1.work_generate_blocking (nano::dev::genesis->hash ()))
 				 .build ();
 	ASSERT_EQ (nano::block_status::progress, node1.process (send1));
-	system.wallet (0)->send_action (nano::dev::genesis_key.pub, nano::dev::genesis_key.pub, new_balance.number ());
-	ASSERT_TIMELY (2s, node1.active.election (send1->qualified_root ()));
-	auto election = node1.active.election (send1->qualified_root ());
-	ASSERT_NE (nullptr, election);
+	auto send2 = builder.make_block ()
+				 .account (nano::dev::genesis_key.pub)
+				 .previous (send1->hash ())
+				 .representative (nano::dev::genesis_key.pub)
+				 .balance (0)
+				 .link (nano::dev::genesis_key.pub)
+				 .sign (nano::dev::genesis_key.prv, nano::dev::genesis_key.pub)
+				 .work (*node1.work_generate_blocking (send1->hash ()))
+				 .build ();
+	ASSERT_EQ (nano::block_status::progress, node1.process (send2));
+	ASSERT_EQ (0, node1.weight (nano::dev::genesis_key.pub));
+	// Insert the voting key only after genesis is drained, so it can never vote on the election while it still holds weight
+	system.wallet (0)->insert_adhoc (nano::dev::genesis_key.prv);
+	node1.start_election (send1);
+	std::shared_ptr<nano::election> election;
+	ASSERT_TIMELY (5s, election = node1.active.election (send1->qualified_root ()));
 	ASSERT_FALSE (election->confirmed ());
 	ASSERT_EQ (1, election->votes ().size ());
 	ASSERT_EQ (0, node1.balance (nano::dev::genesis_key.pub));
```
