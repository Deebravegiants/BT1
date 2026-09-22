# [C] 5.1.2 Memory alignment malleability

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** zkevm-proverjs:sm_mem_align.js#L
**Description:** The constant polynomialBYTE_C4096does not wrap around after value 255 as it should, allowing
inVto have values above a byte, which may carry over and cause anMSTORE8to write a 1 before the given byte in
memory.
Background:Solidity code generation always tries to align memory offsets (such as allocation is done at word-
boundaries) and many other projects writing inline assembly are encouraged to do so. However, some people
optimising for gas do not that, and also it cannot be known for certain that no unaligned case exists in Solidity’s
code generator.
Now imagine if "fake value" insertion is possible in unalignedMLOADs, that means a malicious block builder could
make a user lose or gain value in for example an AMM transaction or other kinds of swaps. Such transactions
could be sandwiches to extract value. Cases of unaligned reads could be easily mapped out by transaction tracing
and "searchers" could build up a database of proof patterns to modify for automatic execution of such malicious
trades.
**Recommendation:** Wrap around after value 255.


```
@@ -11,7 +11,7 @@ const CONST_F = {
BYTE2B: (i) => (i & 0xFF), // [0..255]
// 0 (x4096), 1 (x4096), ..., 255 (x4096), 0 (x4096), ...
```
- BYTE_C4096: (i) => (i >> 12), // [0:4096..255:4096]
+ BYTE_C4096: (i) => (i >> 12) & 0xFF, // [0:4096..255:4096]
    // 0 - 1023 WR256 = 0 WR8 = 0 i & 0xC00 = 0x
    // 1024 - 2047 WR256 = 0 WR8 = 0 i & 0xC00 = 0x

**Polygon-Hermez:** Fixed in PR #116.
**Spearbit:** Acknowledged.
