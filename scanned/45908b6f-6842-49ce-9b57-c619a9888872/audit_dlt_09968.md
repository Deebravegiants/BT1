# [?] fuzz: fix crash on null pointer in witness_program target

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2025-02-08
Source: https://github.com/ElementsProject/elements/commit/86d740b5eb7b365648e8ee379819e1f8337cddc2
Type: security-commit

## Details
fuzz: fix crash on null pointer in witness_program target

## Patch
### src/test/fuzz/witness_program.cpp
```diff
@@ -64,7 +64,7 @@ FUZZ_TARGET_INIT(witness_program, initialize_witness_program)
 
         if (fuzz_control & 1) {
             unsigned char hash_program[32];
-            CSHA256().Write(&program[0], program.size()).Finalize(hash_program);
+            CSHA256().Write(program.data(), program.size()).Finalize(hash_program);
             CScript scriptPubKey = CScript{} << OP_0 << std::vector<unsigned char>(hash_program, hash_program + sizeof(hash_program));
             witness.stack.push_back(program);
 
```
