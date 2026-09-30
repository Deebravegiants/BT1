# [?] fix(circle): add debug_assert for usize underflow in Point methods (#1445)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-03-31
Source: https://github.com/Plonky3/Plonky3/commit/9d6f6654bfe0c15540abbfe02b423a7368a85a25
Type: security-commit

## Details
fix(circle): add debug_assert for usize underflow in Point methods (#1445)

* fix(circle): add debug_assert for usize underflow in Point methods

* add unit tests

* fix: relax debug_assert bounds for s_p_at_p and v_n_prod

s_p_at_p is valid for log_n >= 1 (not >= 2), and v_n_prod handles
log_n <= 1 via early return, so the debug_assert was too strict and
caused periodic_air_circle_prove_verify to fail in CI.

## Patch
### circle/src/point.rs
```diff
@@ -71,6 +71,7 @@ impl<F: Field> Point<F> {
     /// at this point
     /// Circle STARKs, Section 3.3, Equation 8 (page 10 of the first revision PDF)
     pub fn v_n(mut self, log_n: usize) -> F {
+        debug_assert!(log_n >= 1, "v_n requires log_n >= 1");
         for _ in 0..log_n.saturating_sub(1) {
             self.x = self.x.square().double() - F::ONE; // TODO: replace this by a custom field impl.
         }
@@ -104,6 +105,7 @@ impl<F: Field> Point<F> {
     /// The concrete value of the selector s_P = v_n / (v_0 . T_p⁻¹) at P=self, used for normalization.
     /// Circle STARKs, Section 5.1, Remark 16 (page 22 of the first revision PDF)
     pub fn s_p_at_p(self, log_n: usize) -> F {
+        debug_assert!(log_n >= 1, "s_p_at_p requires log_n >= 1");
         -self.v_n_prod(log_n).mul_2exp_u64((2 * log_n - 1) as u64) * self.y
     }
 
@@ -227,4 +229,18 @@ mod tests {
         let vn_prod_gen = (1..log_n).map(|i| generator.v_n(i)).product();
         assert_eq!(generator.v_n_prod(log_n), vn_prod_gen);
     }
+
+    #[test]
+    #[should_panic(expected = "v_n requires log_n >= 1")]
+    fn test_v_n_underflow_log_n_0() {
+        let p = Pt::generator(3);
+        let _ = p.v_n(0);
+    }
+
+    #[test]
+    #[should_panic(expected = "s_p_at_p requires log_n >= 1")]
+    fn test_s_p_at_p_underflow_log_n_0() {
+        let p = Pt::generator(3);
+        let _ = p.s_p_at_p(0);
+    }
 }
```
