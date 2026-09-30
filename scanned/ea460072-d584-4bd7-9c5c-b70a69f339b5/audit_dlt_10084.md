# [?] Fix crash when announcing votes (#1501)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-12-28
Source: https://github.com/nanocurrency/nano-node/commit/074ba488af5c917f22a1b846b79390e17638096c
Type: security-commit

## Details
Fix crash when announcing votes (#1501)

## Patch
### rai/node/node.cpp
```diff
@@ -3325,6 +3325,12 @@ void rai::active_transactions::announce_votes (std::unique_lock<std::mutex> & lo
 					}
 					if (rep_votes.find (rep_acct) != rep_votes.end ())
 					{
+						if (j + 1 == reps->end ())
+						{
+							reps->pop_back ();
+							break;
+						}
+
 						std::swap (*j, reps->back ());
 						reps->pop_back ();
 						m = reps->end ();
```
