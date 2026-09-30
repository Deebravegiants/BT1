# [?] Correctly panic when dividing by zero poly

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2023-11-03
Source: https://github.com/AleoNet/snarkVM-test/commit/7cf307f81874dfec2e910567c13412b6fb195d3e
Type: security-commit

## Details
Correctly panic when dividing by zero poly

## Patch
### algorithms/src/fft/polynomial/mod.rs
```diff
@@ -210,10 +210,10 @@ impl<'a, F: Field> Polynomial<'a, F> {
 
     /// Divide self by another (sparse or dense) polynomial, and returns the quotient and remainder.
     pub fn divide_with_q_and_r(&self, divisor: &Self) -> Option<(DensePolynomial<F>, DensePolynomial<F>)> {
-        if self.is_zero() {
-            Some((DensePolynomial::zero(), DensePolynomial::zero()))
-        } else if divisor.is_zero() {
+        if divisor.is_zero() {
             panic!("Dividing by zero polynomial")
+        } else if self.is_zero() {
+            Some((DensePolynomial::zero(), DensePolynomial::zero()))
         } else if self.degree() < divisor.degree() {
             Some((DensePolynomial::zero(), self.clone().into()))
         } else {
```
