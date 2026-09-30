# [?] Fixing deadlock while flushing blocks.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-01-01
Source: https://github.com/nanocurrency/nano-node/commit/a80a9c0d46e7dfe9a4e1d97806fe23ce47e24abb
Type: security-commit

## Details
Fixing deadlock while flushing blocks.

## Patch
### rai/node/bootstrap.cpp
```diff
@@ -895,7 +895,9 @@ void rai::bootstrap_attempt::run ()
 		}
 		// Flushing may resolve forks which can add more pulls
 		BOOST_LOG (node->log) << "Flushing unchecked blocks";
+		lock.unlock ();
 		node->block_processor.flush ();
+		lock.lock ();
 		BOOST_LOG (node->log) << "Finished flushing unchecked blocks";
 	}
 	if (!stopped)
```
