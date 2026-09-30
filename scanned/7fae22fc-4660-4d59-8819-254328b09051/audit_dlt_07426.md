# [?] Double Spend Proof (dsproof-beta) deserialization fuzzer

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-01-25
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/bac0b6447abfd51f65510ee78a8763cd2ca76cd6
Type: security-commit

## Details
Double Spend Proof (dsproof-beta) deserialization fuzzer

This requires that you have a checkout of the `qa-assets`
repository (https://gitlab.com/bitcoin-cash-node/bchn-sw/qa-assets)

Test plan:

```
FUZZING_SEED_CORPUS_PATH=/path/to/qa-assets/fuzz_seed_corpus
rm -rf build_fuzz && mkdir build_fuzz && cd build_fuzz
cmake -GNinja .. -DENABLE_SANITIZERS="address;fuzzer" \
      -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
ninja bitcoin-fuzzers link-fuzz-test_runner.py
./test/fuzz/test_runner.py -l DEBUG $FUZZING_SEED_CORPUS_PATH
```

For longer fuzzing of the DSP deserializer, run the generated
binary standalone after building:

`./src/test/fuzz/dsproof_deserialize`

## Patch
### src/test/fuzz/CMakeLists.txt
```diff
@@ -45,6 +45,7 @@ add_deserialize_fuzz_targets(
 	bloomfilter_deserialize
 	coins_deserialize
 	diskblockindex_deserialize
+	dsproof_deserialize
 	inv_deserialize
 	messageheader_deserialize
 	netaddr_deserialize
```

### src/test/fuzz/deserialize.cpp
```diff
@@ -8,6 +8,7 @@
 #include <coins.h>
 #include <compressor.h>
 #include <consensus/merkle.h>
+#include <dsproof/dsproof.h>
 #include <net.h>
 #include <primitives/block.h>
 #include <protocol.h>
@@ -180,6 +181,13 @@ void test_one_input(std::vector<uint8_t> buffer) {
     } catch (const std::ios_base::failure &e) {
         return;
     }
+#elif DSPROOF_DESERIALIZE
+    try {
+        DoubleSpendProof dsp;
+        ds >> dsp;
+    } catch (const std::ios_base::failure &e) {
+        return;
+    }
 #else
 #error Need at least one fuzz target to compile
 #endif
```
