# [?] CHIA-1465 Simplify double spend validation in validate_block_body (#18628)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2024-09-26
Source: https://github.com/Chia-Network/chia-blockchain/commit/4383b6f9304abae3b52f4dd514bcd7c99e9e0be5
Type: security-commit

## Details
CHIA-1465 Simplify double spend validation in validate_block_body (#18628)

Simplify double spend validation in validate_block_body.

## Patch
### chia/consensus/block_body_validation.py
```diff
@@ -367,8 +367,8 @@ async def validate_block_body(
 
     # 14. Check for duplicate spends inside block
     removal_counter = collections.Counter(removals)
-    for k, v in removal_counter.items():
-        if v > 1:
+    for count in removal_counter.values():
+        if count > 1:
             return Err.DOUBLE_SPEND, None
 
     # 15. Check if removals exist and were not previously spent. (unspent_db + diff_store + this_block)
```
