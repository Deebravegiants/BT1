# [M] `validateSignature

## Summary
Severity: Medium
Contest weight: 0.1437
Dataset id: 18376
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the validateSignature routine of the EllipticCurve contract used by the DNSSEC oracle. The function mixes affine and projective coordinate handling incorrectly: after adding two affine points it converts them to projective form but then immediately applies an inverse modulo on the Z coordinate even though the Z coordinate is always 1. The code also squares the inverse (mulmod(Px, Px, p)) which is redundant because Px equals 1. As a result the final comparison uses Px % n == rs[0] where Px is effectively the X coordinate multiplied by 1, but the extra operations mask a logical flaw: if the surrounding bug that forces Z to be zero is removed, the function would compute an incorrect X value and reject every signature. The root cause is a misunderstanding of coordinate systems and unnecessary modular inverses, leading to a validation routine that can return false for all inputs once the compensating bug is fixed. Exploitation would consist of an attacker triggering the fix of the compensating bug (or deploying a patched version) and then submitting valid signatures that are incorrectly rejected, causing the protocol to consider legitimate actions unauthenticated. The impact is a denial‑of‑service on any functionality that relies on DNSSEC signatures, such as name resolution or oracle updates, potentially halting the protocol’s operation. The condition occurs only after the other issue that forces the Z coordinate to zero is eliminated; otherwise the bug is effectively neutralized. All users, contract callers, and the protocol itself are affected because they would receive error responses instead of successful verification, leading to missing updates or failed transactions. The issue was discovered during a manual code audit that highlighted the redundant conversion chain and the constant‑one Z coordinate. It is hard to notice because the function still returns true for test vectors when the compensating bug is present, and the redundant arithmetic does not change the result, so unit tests may pass. The proper fix is to remove the unnecessary inverse and squaring, and to compare the X coordinate directly against the signature component, i.e., return P[0] % n == rs[0], and to refactor the point addition to stay in projective form until the final conversion. This aligns the implementation with standard elliptic‑curve verification logic and eliminates the hidden dependency on a separate bug. In user‑facing terms, a user would expect a valid signature to be accepted but would instead see the transaction revert or receive a “signature verification failed” error, effectively making the service unavailable. The bug belongs to the class of cryptographic verification logic errors caused by incorrect handling of coordinate representations.

## Recommendation
To just fix this bug:

```diff
diff --git a/contracts/dnssec-oracle/algorithms/EllipticCurve.sol b/contracts/dnssec-oracle/algorithms/EllipticCurve.sol
index 6861264..ea7e865 100644
--- a/contracts/dnssec-oracle/algorithms/EllipticCurve.sol
+++ b/contracts/dnssec-oracle/algorithms/EllipticCurve.sol
@@ -412,7 +412,7 @@ contract EllipticCurve {
         }

         uint256 Px = inverseMod(P[2], p);
-        Px = mulmod(P[0], mulmod(Px, Px, p), p);
+        Px = mulmod(P[0], Px, p);

         return Px % n == rs[0];
     }
```

Or to fix this bug and optimize out the redundant conversions chain:

```diff
diff --git a/contracts/dnssec-oracle/algorithms/EllipticCurve.sol b/contracts/dnssec-oracle/algorithms/EllipticCurve.sol
index 6861264..8568be2 100644
--- a/contracts/dnssec-oracle/algorithms/EllipticCurve.sol
+++ b/contracts/dnssec-oracle/algorithms/EllipticCurve.sol
@@ -405,14 +405,13 @@ contract EllipticCurve {
         uint256 sInv = inverseMod(rs[1], n);
         (x1, y1) = multiplyScalar(gx, gy, mulmod(uint256(message), sInv, n));
         (x2, y2) = multiplyScalar(Q[0], Q[1], mulmod(rs[0], sInv, n));
-        uint256[3] memory P = addAndReturnProjectivePoint(x1, y1, x2, y2);
+        (uint256 Px,, uint256 Pz) = addProj(x1, y1, 1, x2, y2, 1);

-        if (P[2] == 0) {
+        if (Pz == 0) {
             return false;
         }

-        uint256 Px = inverseMod(P[2], p);
-        Px = mulmod(P[0], mulmod(Px, Px, p), p);
+        Px = mulmod(Px, inverseMod(Pz, p), p);

         return Px % n == rs[0];
     }
```

I agree that EllipticCurve.sol is somewhat of a bodge. It’s correct what the warden says in that ”`EllipticCurve` mixes up” something. But actually it adds affine points and then trivially converts them to jacobian/projective coordinates. Since they are trivial they are the same in jacobian as in projective, so one could say that it’s as much a misnamed function as a confused computation.

But it’s also correct what the warden himself said that it is “currently not exploitable”. In fact, I’m quite sure it’s not exploitable even if “the other issue is fixed”. Then it will just invalidate every signature.

Both recommendations here are therefore just gas savings and refactoring. `mulmod(Px, Px, p)` is indeed a redundant computation, because `Px == 1` always here. But so is `inverseMod(P[2], p)` redundant. The first recommendation can be simplified even further to just

    - uint256 Px = inverseMod(P[2], p);
    - Px = mulmod(P[0], mulmod(Px, Px, p), p);
     
    - return Px % n == rs[0];
    + return P[0] % n == rs[0];

instead, since `P[2] == 1`.

The second recommendation is a better optimisation but still does redundant conversions in `multiplyScalar`, which also should be corrected then. The whole point of using projective coordinates is to do the modular inverse (i.e. convert to affine) only at the end.

In any case, there is nothing exploitable here, no funds or functionality are at risk. The code does what it’s supposed to do as it is, just not in the prettiest way. And the way in which the hypothetical issue is proposed to arise is by fixing the very same thing that the hypothetical issue is itself based on, i.e. it is said that fixing the needless conversion between coordinate representations causes an error due to coordinate conversions. One should assume that reworking the coordinate handling would fix all coordinate issues. And if the bug described here were to arise in the suggested manner, it would be immediately noticed in testing.

_This is a bug that is not yet a bug but could be a bug that is impossible to miss if someone were to create this bug so it’s never going to actually be a bug._

I think this is a good catch, but the severity is only QA/Gas.

I agree with @d3e4 that the bug is highly unlikely to make it to production without being caught. In this case, however, if it were to make it into production, the “function of the protocol or availability could be impacted”. That makes this a valid medium in my view. I agree with the warden and sponsor.
