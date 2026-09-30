# [?] Merge bitcoin/bitcoin#24214: Fix unsigned integer overflows in interpreter

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2024-10-30
Source: https://github.com/ElementsProject/elements/commit/f07a533dfcb172321972e5afb3b38a4bd24edb87
Type: security-commit

## Details
Merge bitcoin/bitcoin#24214: Fix unsigned integer overflows in interpreter

bbbbaa0d9ac9ae9c9b8109503aa30213eed543b9 Fix unsigned integer overflows in interpreter (MarcoFalke)

Pull request description:

  Unsigned integer overflow is well defined by the language and in some cases even useful or necessary. However, I think that it should be avoided in interpreter, as it makes the code harder to read and requires the whole file to be suppressed in the sanitizer. This puts more burden on reviewers to check that any changes to interpreter that involve unsigned integer overflow are sane.

  This patch involves a few changes:
  * Evaluate the addition in 64-bit "space". Previously, the first argument was `size_t` (unsigned, 32-bit or 64-bit, depending on platform) and the second was `int` (32-bit on all supported platforms). Thus the addition was done in 32-bit or 64-bit "unsigned space". Now the addition is done in 64-bit "signed space" on all platforms. This is safe because signed integer overflow (UB) isn't expected here with 64-bit integers.
  * Clarify that the value passed to the "stack macros" always fits in an `int64_t`. This is done with the C++11 syntax `int64_t{i}`, which fails to compile if `i` needs to be narrowed to fit into `int64_t`.
  * Explicitly convert the result of the addition to `size_t`. This isn't needed, because the called function already converts the value (see https://en.cppreference.com/w/cpp/container/vector/operator_at), however I have a slight preference for the explicit cast. (Happy to remove if reviewers prefer without)

  The patch does not change the bitcoind binary on my 64-bit system with `clang++ -O2`. However, it does change with gcc.

ACKs for top commit:
  achow101:
    ACK bbbbaa0d9ac9ae9c9b8109503aa30213eed543b9
  ismaelsadeeq:
    Code review ACK bbbbaa0d9ac9ae9c9b8109503aa30213eed543b9
  hebasto:
    ACK bbbbaa0d9ac9ae9c9b8109503aa30213eed543b9, I have reviewed the code and it looks OK.

Tree-SHA512: 0e9cbc6a0afd3db0d1d9489fd5e32ff856217604abde370add1f01c2cae8c526f2afedeb372997217c3a70ab0f8f56442e8230f87456f8e21c9abcb7c6578f7c

## Patch
### src/script/interpreter.cpp
```diff
@@ -51,8 +51,8 @@ bool CastToBool(const valtype& vch)
  * Script is a stack machine (like Forth) that evaluates a predicate
  * returning a bool indicating valid or not.  There are no loops.
  */
-#define stacktop(i)  (stack.at(stack.size()+(i)))
-#define altstacktop(i)  (altstack.at(altstack.size()+(i)))
+#define stacktop(i) (stack.at(size_t(int64_t(stack.size()) + int64_t{i})))
+#define altstacktop(i) (altstack.at(size_t(int64_t(altstack.size()) + int64_t{i})))
 static inline void popstack(std::vector<valtype>& stack)
 {
     if (stack.empty())
```

### test/sanitizer_suppressions/ubsan
```diff
@@ -55,7 +55,6 @@ unsigned-integer-overflow:MurmurHash3
 unsigned-integer-overflow:CBlockPolicyEstimator::processBlockTx
 unsigned-integer-overflow:TxConfirmStats::EstimateMedianVal
 unsigned-integer-overflow:prevector.h
-unsigned-integer-overflow:EvalScript
 unsigned-integer-overflow:InsecureRandomContext::rand64
 unsigned-integer-overflow:InsecureRandomContext::SplitMix64
 unsigned-integer-overflow:bitset_detail::PopCount
```
