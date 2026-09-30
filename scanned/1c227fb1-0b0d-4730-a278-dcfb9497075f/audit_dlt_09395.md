# [?] avoid signed integer overflow

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2022-03-09
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/322c1d0bab16b9662bfedc53382aa7af1c522e2f
Type: security-commit

## Details
avoid signed integer overflow

## Patch
### src/test/op_reversebytes_tests.cpp
```diff
@@ -104,7 +104,7 @@ BOOST_AUTO_TEST_CASE(op_reversebytes_random_and_palindrome) {
         MANDATORY_SCRIPT_VERIFY_FLAGS,
     });
     for (uint32_t flagindex = 0; flagindex < 32; ++flagindex) {
-        uint32_t flags = 1 << flagindex;
+        uint32_t flags = 1u << flagindex;
         flaglist.push_back(flags);
     }
 
```
