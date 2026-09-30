# [?] Fix ledger processor hash2 race condition

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-02-11
Source: https://github.com/nanocurrency/nano-node/commit/c42d669769692ddacfca38ef4d5153b8d94de1b4
Type: security-commit

## Details
Fix ledger processor hash2 race condition

## Patch
### rai/secure.cpp
```diff
@@ -2660,7 +2660,12 @@ void ledger_processor::change_block (rai::change_block const & block_a)
 				result.code = validate_message (account, hash, block_a.signature) ? rai::process_result::bad_signature : rai::process_result::progress; // Is this block signed correctly (Malformed)
 				if (result.code == rai::process_result::progress)
 				{
-					assert (!hash2.is_zero ());
+					if (hash2.is_zero ())
+					{
+						// recalculate hash2 to prevent race condition
+						hash2 = ledger.store.hash2_calc (transaction, block_a);
+						assert (!hash2.is_zero ());
+					}
 					ledger.store.hash2_put (transaction, hash, hash2);
 					ledger.store.block_put (transaction, hash2, block_a);
 					auto balance (ledger.balance (transaction, block_a.hashables.previous));
@@ -2703,7 +2708,12 @@ void ledger_processor::send_block (rai::send_block const & block_a)
 					result.code = info.balance.number () >= block_a.hashables.balance.number () ? rai::process_result::progress : rai::process_result::negative_spend; // Is this trying to spend a negative amount (Malicious)
 					if (result.code == rai::process_result::progress)
 					{
-						assert (!hash2.is_zero ());
+						if (hash2.is_zero ())
+						{
+							// recalculate hash2 to prevent race condition
+							hash2 = ledger.store.hash2_calc (transaction, block_a);
+							assert (!hash2.is_zero ());
+						}
 						ledger.store.hash2_put (transaction, hash, hash2);
 						auto amount (info.balance.number () - block_a.hashables.balance.number ());
 						ledger.store.representation_add (transaction, info.rep_block, 0 - amount);
@@ -2754,7 +2764,12 @@ void ledger_processor::receive_block (rai::receive_block const & block_a)
 							rai::account_info source_info;
 							auto error (ledger.store.account_get (transaction, pending.source, source_info));
 							assert (!error);
-							assert (!hash2.is_zero ());
+							if (hash2.is_zero ())
+							{
+								// recalculate hash2 to prevent race condition
+								hash2 = ledger.store.hash2_calc (transaction, block_a);
+								assert (!hash2.is_zero ());
+							}
 							ledger.store.hash2_put (transaction, hash, hash2);
 							ledger.store.pending_del (transaction, key);
 							ledger.store.block_put (transaction, hash, block_a);
@@ -2806,7 +2821,12 @@ void ledger_processor::open_block (rai::open_block const & block_a)
 							rai::account_info source_info;
 							auto error (ledger.store.account_get (transaction, pending.source, source_info));
 							assert (!error);
-							assert (!hash2.is_zero ());
+							if (hash2.is_zero ())
+							{
+								// recalculate hash2 to prevent race condition
+								hash2 = ledger.store.hash2_calc (transaction, block_a);
+								assert (!hash2.is_zero ());
+							}
 							ledger.store.pending_del (transaction, key);
 							ledger.store.hash2_put (transaction, hash, hash2);
 							ledger.store.block_put (transaction, hash, block_a);
```
