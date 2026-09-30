# [?] Merge pull request #537 from zcash/fix-stack-overflow

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/halo2
Published: 2022-04-04
Source: https://github.com/privacy-ethereum/halo2/commit/95df0af86dab803ca5dea5586dae15d9b2f75394
Type: security-commit

## Details
Merge pull request #537 from zcash/fix-stack-overflow

Reduce depth of AST by special casing the application of Horner's rule

## Patch
### halo2_proofs/CHANGELOG.md
```diff
@@ -7,6 +7,10 @@ and this project adheres to Rust's notion of
 
 ## [Unreleased]
 
+### Changed
+- PLONK prover was improved to avoid stack overflows when large numbers of gates
+  are involved in a proof.
+
 ## [0.1.0-beta.3] - 2022-03-22
 ### Added
 - `halo2_proofs::circuit`:
```

### halo2_proofs/src/plonk/vanishing/prover.rs
```diff
@@ -77,9 +77,7 @@ impl<C: CurveAffine> Committed<C> {
         transcript: &mut T,
     ) -> Result<Constructed<C>, Error> {
         // Evaluate the h(X) polynomial's constraint system expressions for the constraints provided
-        let h_poly = expressions
-            .reduce(|h_poly, v| &(&h_poly * *y) + &v) // Fold the gates together with the y challenge
-            .unwrap_or_else(|| poly::Ast::ConstantTerm(C::Scalar::zero()));
+        let h_poly = poly::Ast::distribute_powers(expressions, *y); // Fold the gates together with the y challenge
         let h_poly = evaluator.evaluate(&h_poly, domain); // Evaluate the h(X) polynomial
 
         // Divide by t(X) = X^{params.n} - 1.
```

### halo2_proofs/src/poly/evaluator.rs
```diff
@@ -150,6 +150,10 @@ impl<E, F: Field, B: Basis> Evaluator<E, F, B> {
                     lhs.union(&rhs).cloned().collect()
                 }
                 Ast::Scale(a, _) => collect_rotations(a),
+                Ast::DistributePowers(terms, _) => terms
+                    .iter()
+                    .flat_map(|term| collect_rotations(term).into_iter())
+                    .collect(),
                 Ast::LinearTerm(_) | Ast::ConstantTerm(_) => HashSet::default(),
             }
         }
@@ -225,6 +229,17 @@ impl<E, F: Field, B: Basis> Evaluator<E, F, B> {
                     }
                     lhs
                 }
+                Ast::DistributePowers(terms, base) => terms.iter().fold(
+                    B::constant_term(ctx.poly_len, ctx.chunk_size, ctx.chunk_index, F::zero()),
+                    |mut acc, term| {
+                        let term = recurse(term, ctx);
+                        for (acc, term) in acc.iter_mut().zip(term) {
+                            *acc *= base;
+                            *acc += term;
+                        }
+                        acc
+                    },
+                ),
                 Ast::LinearTerm(scalar) => B::linear_term(
                     ctx.domain,
                     ctx.poly_len,
@@ -285,6 +300,10 @@ pub(crate) enum Ast<E, F: Field, B: Basis> {
     Add(Arc<Ast<E, F, B>>, Arc<Ast<E, F, B>>),
     Mul(AstMul<E, F, B>),
     Scale(Arc<Ast<E, F, B>>, F),
+    /// Represents a linear combination of a vector of nodes and the powers of a
+    /// field element, where the nodes are ordered from highest to lowest degree
+    /// terms.
+    DistributePowers(Arc<Vec<Ast<E, F, B>>>, F),
     /// The degree-1 term of a polynomial.
     ///
     /// The field element is the coefficient of the term in the standard basis, not the
@@ -296,13 +315,24 @@ pub(crate) enum Ast<E, F: Field, B: Basis> {
     ConstantTerm(F),
 }
 
+impl<E, F: Field, B: Basis> Ast<E, F, B> {
+    pub fn distribute_powers<I: IntoIterator<Item = Self>>(i: I, base: F) -> Self {
+        Ast::DistributePowers(Arc::new(i.into_iter().collect()), base)
+    }
+}
+
 impl<E, F: Field, B: Basis> fmt::Debug for Ast<E, F, B> {
     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
         match self {
             Self::Poly(leaf) => f.debug_tuple("Poly").field(leaf).finish(),
             Self::Add(lhs, rhs) => f.debug_tuple("Add").field(lhs).field(rhs).finish(),
             Self::Mul(x) => f.debug_tuple("Mul").field(x).finish(),
             Self::Scale(base, scalar) => f.debug_tuple("Scale").field(base).field(scalar).finish(),
+            Self::DistributePowers(terms, base) => f
+                .debug_tuple("DistributePowers")
+                .field(terms)
+                .field(base)
+                .finish(),
             Self::LinearTerm(x) => f.debug_tuple("LinearTerm").field(x).finish(),
             Self::ConstantTerm(x) => f.debug_tuple("ConstantTerm").field(x).finish(),
         }
```
