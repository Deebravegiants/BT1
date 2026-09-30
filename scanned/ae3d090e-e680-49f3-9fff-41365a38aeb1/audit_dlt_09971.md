# [?] Fix unsigned integer overflows in interpreter

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2022-01-31
Source: https://github.com/ElementsProject/elements/commit/bbbbaa0d9ac9ae9c9b8109503aa30213eed543b9
Type: security-commit

## Details
Fix unsigned integer overflows in interpreter

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
