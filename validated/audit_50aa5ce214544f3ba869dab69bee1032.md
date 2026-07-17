### Title
Missing G2 Subgroup Membership Check in `alt_bn128_pairing_check` Allows Forged ZK Proof Acceptance - (`runtime/near-vm-runner/src/logic/alt_bn128.rs`)

### Summary

`decode_g2` only validates that a supplied G2 point satisfies the twist curve equation. It performs no prime-order subgroup membership check. Because the BN128 twist `E'(Fq2)` has a non-trivial cofactor `h2`, an attacker can supply a point of order dividing `h2` that passes `AffineG2::new` but causes `bn::pairing_batch` to return `Gt::one()` for any G1 counterpart, making `pairing_check` return `true` unconditionally.

### Finding Description

`decode_g2` calls `bn::AffineG2::new(x, y)`, which only verifies the point satisfies `Y^2 = X^3 + 3/(i+9)` over `Fq2`. It does not multiply the candidate point by `r` (the prime group order) to confirm the result is the point at infinity, which is the standard subgroup membership test. [1](#0-0) 

`pairing_check` then passes the unvalidated point directly to `bn::pairing_batch` and compares the result to `bn::Gt::one()`. [2](#0-1) 

The host function documentation explicitly promises that a point "not in the subgroup" returns `AltBn128InvalidInput`, but the implementation never enforces this. [3](#0-2) 

### Impact Explanation

For BN128, `#E'(Fq2) = r * h2` where `r` is prime and `gcd(r, h2) = 1`. Any point `Q` of order dividing `h2` satisfies:

```
e(P, Q)^{h2} = e(P, h2·Q) = e(P, O) = 1
```

So `e(P, Q)` is an `h2`-th root of unity in `GT`. Since `GT` has prime order `r` and `gcd(r, h2) = 1`, the only such root is `1`. Therefore `bn::pairing_batch` returns `Gt::one()` for **any** G1 point paired with a cofactor-order G2 point, and `pairing_check` returns `true`.

Any NEAR smart contract using `alt_bn128_pairing_check` as a Groth16 or PLONK verifier will accept a forged proof whose G2 component is replaced with a cofactor-order point. This allows an unprivileged user to trigger arbitrary state transitions gated behind ZK proof validity (e.g., unauthorized token mints, bridge withdrawals, private-state updates).

### Likelihood Explanation

The attack is straightforward:
1. Pick any random point `T` on `E'(Fq2)`.
2. Compute `Q = r * T`. This is in the cofactor subgroup (order divides `h2`).
3. Encode `Q` as a 128-byte little-endian input.
4. Call any contract that invokes `alt_bn128_pairing_check` with `Q` as the G2 component.

No privileged access is required. The attacker only needs to submit a transaction calling a vulnerable contract. The `bn` crate's `AffineG2::new` will accept `Q` (it is on the curve), and the pairing will return `Gt::one()`.

### Recommendation

Add a subgroup membership check in `decode_g2` after the curve-membership check:

```rust
fn decode_g2(raw: &[u8; 2 * POINT_SIZE]) -> Result<bn::G2, InvalidInput> {
    // ... existing curve check ...
    let point = bn::AffineG2::new(x, y)
        .map_err(|_err| InvalidInput::new("invalid g2", raw))
        .map(bn::G2::from)?;
    // Subgroup check: r * point must be the point at infinity
    if bn::G2::mul(point, bn::Fr::one()) /* or explicit r-multiplication */ != bn::G2::zero() {
        return Err(InvalidInput::new("g2 point not in prime-order subgroup", raw));
    }
    Ok(point)
}
```

Alternatively, use the endomorphism-based subgroup check (multiply by the curve's `h2` cofactor and verify the result equals the original point scaled appropriately), which is faster than a full scalar multiplication by `r`.

Note the contrast with the BLS12-381 implementation, which explicitly calls `blst_p2_affine_in_g2` before proceeding: [4](#0-3) 

### Proof of Concept

```rust
// Pseudocode: construct a cofactor-order G2 point and verify pairing_check returns true
let r = BN128_PRIME_ORDER; // the scalar field prime
let T = random_twist_point(); // any point on E'(Fq2)
let Q = T * r;               // Q is now in the cofactor subgroup, order divides h2
assert!(Q != G2::zero());    // Q is non-trivial

let P = G1::generator();
let result = alt_bn128_pairing_check(encode(P, Q));
assert_eq!(result, 1); // returns "true" — forged proof accepted
```

Enumerate small-order points by multiplying random twist points by `r`, encode as 128-byte little-endian, and assert `pairing_check` always returns `1` (true) for such inputs paired with any non-identity G1 point. [1](#0-0)

### Citations

**File:** runtime/near-vm-runner/src/logic/alt_bn128.rs (L77-93)
```rust
pub(crate) fn pairing_check(
    elements: &[[u8; PAIRING_CHECK_ELEMENT_SIZE]],
) -> Result<bool, InvalidInput> {
    let elements: Vec<(bn::G1, bn::G2)> = elements
        .iter()
        .map(|chunk| {
            let (g1, g2) = stdx::split_array(chunk);
            let g1 = decode_g1(g1)?;
            let g2 = decode_g2(g2)?;
            Ok((g1, g2))
        })
        .collect::<Result<Vec<_>, InvalidInput>>()?;

    let res = bn::pairing_batch(&elements) == bn::Gt::one();

    Ok(res)
}
```

**File:** runtime/near-vm-runner/src/logic/alt_bn128.rs (L131-142)
```rust
fn decode_g2(raw: &[u8; 2 * POINT_SIZE]) -> Result<bn::G2, InvalidInput> {
    let (x, y) = stdx::split_array(raw);
    let x = decode_fq2(x)?;
    let y = decode_fq2(y)?;
    if x.is_zero() && y.is_zero() {
        Ok(bn::G2::zero())
    } else {
        bn::AffineG2::new(x, y)
            .map_err(|_err| InvalidInput::new("invalid g2", raw))
            .map(bn::G2::from)
    }
}
```

**File:** runtime/near-vm-runner/src/logic/logic.rs (L1112-1114)
```rust
    /// If point coordinates are not on curve, point is not in the subgroup, scalar
    /// is not in the field or data are wrong serialized, for example,
    /// `value.len()%192!=0`, the function returns `AltBn128InvalidInput`.
```

**File:** runtime/near-vm-runner/src/logic/bls12381.rs (L369-372)
```rust
        let g2_check = unsafe { blst::blst_p2_affine_in_g2(&blst_g2_list[i]) };
        if g2_check == false {
            return Ok(1);
        }
```
