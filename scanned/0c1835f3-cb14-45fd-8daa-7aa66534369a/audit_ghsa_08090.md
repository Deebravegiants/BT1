# [M] ml-dsa's UseHint function has off by two error when r0 equals zero

## Summary
Severity: Medium
Advisory: GHSA-h37v-hp6w-2pp8
CWE: CWE-193, CWE-682
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-h37v-hp6w-2pp8
Type: github-advisory

## Affected
- crates.io: `ml-dsa` — affected >=0 <0.1.0-rc.5

## Details
### Summary

There's a bug in the `use_hint` function where it adds 1 instead of subtracting 1 when the decomposed low bits `r0` equal exactly zero. FIPS 204 Algorithm 40 is pretty clear that `r0 > 0` means strictly positive, but the current code treats zero as positive. This causes valid signatures to potentially fail verification when this edge case gets hit.

### Details

The issue is in `ml-dsa/src/hint.rs` in the `use_hint` function. Here's what FIPS 204 Algorithm 40 says:

```
3: if h = 1 and r0 > 0  return (r1 + 1) mod m
4: if h = 1 and r0 <= 0  return (r1 − 1) mod m
```

Line 3 uses `r0 > 0` (strictly greater than zero), and line 4 uses `r0 <= 0` (less than or equal, which includes zero). So when `r0 = 0`, the spec says to subtract 1.

But the current implementation does this:

```rust
if h && r0.0 <= gamma2 {
    Elem::new((r1.0 + 1) % m)
} else if h && r0.0 >= BaseField::Q - gamma2 {
    Elem::new((r1.0 + m - 1) % m)
}
```

The problem is `r0.0 <= gamma2` includes zero. When `r0 = 0`, this condition is true (since `0 <= gamma2`), so it adds 1. But according to the spec, `r0 = 0` should fall into the `r0 <= 0` case and subtract 1 instead.

The result is +1 when it should be -1, which is an off by two error mod m.

### PoC

Take MLDSA 44 where γ2 = 95,232 and m = 44.

If `use_hint(true, 0)` is called:
- `Decompose(0)` gives `(r1=0, r0=0)`
- The condition `r0.0 <= gamma2` is `0 <= 95232` which is true
- So it returns `(0 + 1) % 44 = 1`

But FIPS 204 says:
- `r0 > 0` is `0 > 0` which is false
- `r0 ≤ 0` is `0 ≤ 0` which is true
- So it should return `(0 - 1) mod 44 = 43`

The function returns 1 when it should return 43.

This can happen in real signatures whenever any coefficient of the `w'` vector happens to be a multiple of 2γ2, which makes its decomposed `r0` equal zero. It's not super common but it's definitely possible, and when it hits, verification will fail for a completely valid signature.

### Impact

This is a FIPS 204 compliance bug that affects signature verification. When the edge case triggers, valid signatures get rejected. Since MLDSA is supposed to be used for high security post quantum cryptography, having verification randomly fail isn't great. It's also theoretically possible that the mismatch between what signing expects and what verification does could be exploited somehow, though that would need more looking into.

The fix is straightforward, just change the condition to explicitly check for positive values:

```rust
if h && r0.0 > 0 && r0.0 <= gamma2 {
    Elem::new((r1.0 + 1) % m)
} else if h {
    Elem::new((r1.0 + m - 1) % m)
}
```

## References
- https://github.com/RustCrypto/signatures/security/advisories/GHSA-h37v-hp6w-2pp8
- https://github.com/RustCrypto/signatures/commit/10f4ff04cb43ef2b789ee06e885f11cd054b1335
- https://github.com/RustCrypto/signatures
