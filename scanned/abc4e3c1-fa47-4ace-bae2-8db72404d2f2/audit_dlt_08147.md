# [?] unit_tests: fix crash in debug in output_distribution test

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-04-25
Source: https://github.com/monero-project/monero/commit/a59c27465b12581702d9489e574f92f9141f158a
Type: security-commit

## Details
unit_tests: fix crash in debug in output_distribution test

updating the block size limit needs recent block sizes,
so we feed it dummy ones

## Patch
### tests/unit_tests/output_distribution.cpp
```diff
@@ -62,6 +62,13 @@ class TestDB: public cryptonote::BaseTestDB
     return d;
   }
 
+  std::vector<uint64_t> get_block_weights(uint64_t start_offset, size_t count) const override
+  {
+    std::vector<uint64_t> weights;
+    while (count--) weights.push_back(1);
+    return weights;
+  }
+
   uint64_t blockchain_height;
 };
 
```
