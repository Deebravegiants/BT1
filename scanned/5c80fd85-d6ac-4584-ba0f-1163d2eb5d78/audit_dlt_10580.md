# [?] Fix blogpost link for UnsoundSpillInMutualRecursion bug

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2026-07-08
Source: https://github.com/argotorg/solidity/commit/12f0e96125a14e462247fa9008cace8b8d24f15e
Type: security-commit

## Details
Fix blogpost link for UnsoundSpillInMutualRecursion bug

## Patch
### docs/bugs.json
```diff
@@ -4,7 +4,7 @@
         "name": "UnsoundSpillInMutualRecursion",
         "summary": "Local variables of a function involved in mutual recursion may spuriously be moved to fixed memory offsets and overwritten across recursive calls.",
         "description": "To work around the 16-slot stack access limit of the EVM, the IR-based code generator can move local variables of stack-too-deep functions to fixed memory offsets. This relocation is unsound for recursive functions: a fixed offset would be shared by all activations of the function, so a recursive call would overwrite the caller's value. The stack limit evader therefore must not relocate variables of functions that are part of a recursive call chain. To this end, the call graph was searched for cycles using a path-based depth-first search that, once a function had been fully explored and popped from the search path, short-circuited on it on any later visit. As a result, a function shared between several intersecting cycles could be reached first through a path that did not yet close a cycle through it, get marked as finished, and then be skipped when a later path would have revealed that it does lie on a cycle. Such a function was misclassified as non-recursive. When a misclassified function was complex enough for the stack limit evader to relocate some of its variables, those variables were moved to fixed memory offsets and silently corrupted on recursion, producing wrong results rather than a compile-time error. Triggering the bug requires the IR pipeline, a set of mutually recursive functions whose call graph contains intersecting cycles, at least one of the functions in an undetected part of a cycle being complex enough to require relocation to memory, and an unfortunate processing order of the functions (which depends on the hashes of their Yul names). It is independent of whether the optimizer is enabled.",
-        "link": "https://blog.soliditylang.org/2026/07/08/unsound-spill-in-mutual-recursion-bug/",
+        "link": "https://blog.soliditylang.org/2026/07/09/unsound-spill-in-mutual-recursion-bug/",
         "introduced": "0.7.2",
         "fixed": "0.8.36",
         "severity": "medium",
```
