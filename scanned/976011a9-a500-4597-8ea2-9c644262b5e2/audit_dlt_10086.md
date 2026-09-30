# [?] Fix possible deadlock by not checking shutdown condition after lock is unlocked in send().

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-10-13
Source: https://github.com/nanocurrency/nano-node/commit/75871606a488558054be4f05e1588bd75ebc780e
Type: security-commit

## Details
Fix possible deadlock by not checking shutdown condition after lock is unlocked in send().

## Patch
### rai/node/voting.cpp
```diff
@@ -78,12 +78,15 @@ void rai::vote_generator::run ()
 		}
 		else // now >= cutoff && hashes.size () < 12
 		{
+			cutoff = min;
 			if (!hashes.empty ())
 			{
 				send (lock);
 			}
-			cutoff = min;
-			condition.wait (lock);
+			else
+			{
+				condition.wait (lock);
+			}
 		}
 	}
 }
```
