# [?] doc: Prove that the Merkle mutation check is sufficient (CVE-2012-2459).

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-04-12
Source: https://github.com/zcash/zcash/commit/8f69946f2eee3501cd8241d3e7e325b7bb53998b
Type: security-commit

## Details
doc: Prove that the Merkle mutation check is sufficient (CVE-2012-2459).

Replace the "all known ways" hedge with an informal proof by strong
induction that (root, mutated=false) uniquely determines the
transaction list, assuming no SHA-256d collisions.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### src/consensus/merkle.cpp
```diff
@@ -33,9 +33,32 @@
        valid) versions of the same block. We defend against this by detecting
        the case where we would hash two identical hashes at the end of the list
        together, and treating that identically to the block having an invalid
-       merkle root. Assuming no double-SHA256 collisions, this will detect all
-       known ways of changing the transactions without affecting the merkle
-       root.
+       merkle root.
+
+       Claim: assuming no double-SHA256 collisions, the (root, mutated) pair
+       returned by ComputeMerkleRoot uniquely determines the input hash list
+       when mutated is false.
+
+       Proof by strong induction on max(|L1|, |L2|) for two lists that produce
+       the same root with mutated = false:
+
+       Base (max <= 1): single-element lists with the same root must have the
+       same element; mismatched lengths produce different roots.
+
+       Inductive step (both lists have size >= 2): after one hashing round,
+       L1 and L2 produce intermediate lists M1 and M2 with lengths
+       ceil(|L1|/2) < |L1| and ceil(|L2|/2) < |L2|. Since the overall mutated
+       flag is false, no mutation occurs at any subsequent level either, so by
+       the inductive hypothesis M1 = M2.
+
+       Equal intermediate lengths imply |L1| and |L2| differ by at most 1. If
+       they are equal, collision-freeness of the hash gives L1[i] = L2[i] for
+       each position. If they differ by 1, wlog say |L1| = n-1 (odd) and
+       |L2| = n (even), the last intermediate hash of L1 comes from duplicating
+       its last element: H(L1[n-2] || L1[n-2]) = H(L2[n-2] || L2[n-1]).
+       Collision-freeness gives L2[n-2] = L2[n-1]. But L2 has even length, so
+       (n-2, n-1) is a checked pair in the mutation scan. This pair being equal
+       causes the mutated flag to be set, contradicting the assumption. ∎
 */
 
 
```
