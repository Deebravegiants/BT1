# [?] Clearing roots after thread has joined to avoid a use-after-free situation.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-11-08
Source: https://github.com/nanocurrency/nano-node/commit/c8245e83d9f8e6839961a5164df5ffefb411c5b7
Type: security-commit

## Details
Clearing roots after thread has joined to avoid a use-after-free situation.

Boost multi_index iterators remain valid on insertion but not after erasure.

## Patch
### rai/node/node.cpp
```diff
@@ -3007,13 +3007,13 @@ void rai::active_transactions::stop ()
 			condition.wait (lock);
 		}
 		stopped = true;
-		roots.clear ();
 		condition.notify_all ();
 	}
 	if (thread.joinable ())
 	{
 		thread.join ();
 	}
+	roots.clear ();
 }
 
 bool rai::active_transactions::start (std::shared_ptr<rai::block> block_a, std::function<void(std::shared_ptr<rai::block>)> const & confirmation_action_a)
```
