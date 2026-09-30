# [?] Fix race condition from TSAN where block_sideband is updated by different nodes.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2024-04-09
Source: https://github.com/nanocurrency/nano-node/commit/cb1893a424d407f18a009e682e902d8ea525ea59
Type: security-commit

## Details
Fix race condition from TSAN where block_sideband is updated by different nodes.

## Patch
### nano/core_test/node.cpp
```diff
@@ -647,14 +647,14 @@ TEST (node, fork_keep)
 				 .work (*system.work.generate (nano::dev::genesis->hash ()))
 				 .build ();
 	node1.process_active (send1);
-	node2.process_active (send1);
+	node2.process_active (builder.make_block ().from (*send1).build ());
 	ASSERT_TIMELY_EQ (5s, 1, node1.active.size ());
 	ASSERT_TIMELY_EQ (5s, 1, node2.active.size ());
 	system.wallet (0)->insert_adhoc (nano::dev::genesis_key.prv);
 	// Fill node with forked blocks
 	node1.process_active (send2);
 	ASSERT_TIMELY (5s, node1.active.active (*send2));
-	node2.process_active (send2);
+	node2.process_active (builder.make_block ().from (*send2).build ());
 	ASSERT_TIMELY (5s, node2.active.active (*send2));
 	auto election1 (node2.active.election (nano::qualified_root (nano::dev::genesis->hash (), nano::dev::genesis->hash ())));
 	ASSERT_NE (nullptr, election1);
```

### nano/lib/blockbuilders.cpp
```diff
@@ -516,6 +516,21 @@ nano::send_block_builder::send_block_builder ()
 	make_block ();
 }
 
+nano::send_block_builder & nano::send_block_builder::from (nano::send_block const & other_block)
+{
+	block->work = other_block.work;
+	build_state |= build_flags::work_present;
+	block->signature = other_block.signature;
+	build_state |= build_flags::signature_present;
+	block->hashables.balance = other_block.hashables.balance;
+	build_state |= build_flags::balance_present;
+	block->hashables.destination = other_block.hashables.destination;
+	build_state |= build_flags::link_present;
+	block->hashables.previous = other_block.hashables.previous;
+	build_state |= build_flags::previous_present;
+	return *this;
+}
+
 nano::send_block_builder & nano::send_block_builder::make_block ()
 {
 	construct_block ();
```

### nano/lib/blockbuilders.hpp
```diff
@@ -199,6 +199,8 @@ class send_block_builder : public abstract_builder<nano::send_block, send_block_
 public:
 	/** Creates a send block builder by calling make_block() */
 	send_block_builder ();
+	/** Initialize from an existing block */
+	send_block_builder & from (nano::send_block const & block);
 	/** Creates a new block with fields, signature and work set to sentinel values. All fields must be set or zeroed for build() to succeed. */
 	send_block_builder & make_block ();
 	/** Sets all hashables, signature and work to zero. */
```
