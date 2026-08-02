No vulnerability found for this question.

The `weighted_sum` function in [1](#0-0)  is only invoked from `Reconstructable::reconstruct` in [2](#0-1) , where both `bases` (from `shares[..sc.t]`) and `lagrange_coeffs` (from `sc.lagrange_for_subset(&roots_of_unity_indices)`, computed over the same `sc.t`-length index set) are always constructed with identical length `sc.t` by construction — there is no code path allowing mismatched-length inputs to reach `weighted_sum`. Even hypothetically, this is a low-level arkworks/DKG cryptographic utility, not reachable from an unprivileged transaction, package, view, authenticator, API, bytecode, or proof input as required by the review bounds, and a panic here would at most be a liveness issue in the DKG process rather than a custody-grade impact (theft, mint, burn, freeze, or ownership reassignment) required by the Custody Impact Gate.

### Citations

**File:** crates/aptos-crypto/src/arkworks/weighted_sum.rs (L32-39)
```rust
impl<P: SWCurveConfig> WeightedSum for Affine<P> {
    type Scalar = P::ScalarField;

    fn weighted_sum(bases: &[Self], scalars: &[Self::Scalar]) -> Self {
        <Self as AffineRepr>::Group::msm(bases, scalars)
            .expect("MSM failed weighted_sum()")
            .into()
    }
```

**File:** crates/aptos-crypto/src/arkworks/shamir.rs (L334-360)
```rust
impl<T: WeightedSum> Reconstructable<ShamirThresholdConfig<T::Scalar>> for T {
    type ShareValue = T;

    // Can receive more than `sc.t` shares, but will only use the first `sc.t` shares for efficiency
    fn reconstruct(
        sc: &ShamirThresholdConfig<T::Scalar>,
        shares: &[ShamirShare<Self::ShareValue>],
    ) -> Result<Self> {
        if shares.len() < sc.t {
            Err(anyhow!(
                "Incorrect number of shares provided, received {} but expected at least {}",
                shares.len(),
                sc.t
            ))
        } else {
            let (roots_of_unity_indices, bases): (Vec<usize>, Vec<Self::ShareValue>) = shares
                [..sc.t]
                .iter()
                .map(|(p, g_y)| (p.get_id(), g_y))
                .collect();

            let lagrange_coeffs = sc.lagrange_for_subset(&roots_of_unity_indices);

            Ok(T::weighted_sum(&bases, &lagrange_coeffs))
        }
    }
}
```
