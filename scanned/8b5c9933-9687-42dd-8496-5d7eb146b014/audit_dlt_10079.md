# [?] Fix wallet_republish crash during bootstrap

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2021-01-03
Source: https://github.com/nanocurrency/nano-node/commit/d473d21c51d5b416dc5088850671cda8baf49f46
Type: security-commit

## Details
Fix wallet_republish crash during bootstrap

## Patch
### nano/node/network.cpp
```diff
@@ -219,22 +219,25 @@ void nano::network::flood_vote_pr (std::shared_ptr<nano::vote> const & vote_a)
 
 void nano::network::flood_block_many (std::deque<std::shared_ptr<nano::block>> blocks_a, std::function<void()> callback_a, unsigned delay_a)
 {
-	auto block_l (blocks_a.front ());
-	blocks_a.pop_front ();
-	flood_block (block_l);
 	if (!blocks_a.empty ())
 	{
-		std::weak_ptr<nano::node> node_w (node.shared ());
-		node.alarm.add (std::chrono::steady_clock::now () + std::chrono::milliseconds (delay_a + std::rand () % delay_a), [node_w, blocks (std::move (blocks_a)), callback_a, delay_a]() {
-			if (auto node_l = node_w.lock ())
-			{
-				node_l->network.flood_block_many (std::move (blocks), callback_a, delay_a);
-			}
-		});
-	}
-	else if (callback_a)
-	{
-		callback_a ();
+		auto block_l (blocks_a.front ());
+		blocks_a.pop_front ();
+		flood_block (block_l);
+		if (!blocks_a.empty ())
+		{
+			std::weak_ptr<nano::node> node_w (node.shared ());
+			node.alarm.add (std::chrono::steady_clock::now () + std::chrono::milliseconds (delay_a + std::rand () % delay_a), [node_w, blocks (std::move (blocks_a)), callback_a, delay_a]() {
+				if (auto node_l = node_w.lock ())
+				{
+					node_l->network.flood_block_many (std::move (blocks), callback_a, delay_a);
+				}
+			});
+		}
+		else if (callback_a)
+		{
+			callback_a ();
+		}
 	}
 }
 
```
