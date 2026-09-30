# [?] Fixing thread sanitizer data race condition.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-08-22
Source: https://github.com/nanocurrency/nano-node/commit/096d2f2d1c5c8ac88307c01f4dbf7b5f1d17b780
Type: security-commit

## Details
Fixing thread sanitizer data race condition.

## Patch
### rai/core_test/rpc.cpp
```diff
@@ -1432,7 +1432,7 @@ TEST (rpc, work_peer_bad)
 	rpc.start ();
 	node2.config.work_peers.push_back (std::make_pair (boost::asio::ip::address_v6::any (), 0));
 	rai::block_hash hash1 (1);
-	uint64_t work (0);
+	std::atomic <uint64_t> work (0);
 	node2.generate_work (hash1, [&work] (uint64_t work_a)
 	{
 		work = work_a;
```
