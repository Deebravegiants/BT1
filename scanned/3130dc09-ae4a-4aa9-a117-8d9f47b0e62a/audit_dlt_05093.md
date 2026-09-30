# [?] fix(polynomials): avoid out-of-bounds intermediate pointer in token-indexed accessors

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-06-25
Source: https://github.com/AztecProtocol/aztec-packages/commit/0ccc236fe4492a2f9e3e50d659677ad342b1baef
Type: security-commit

## Details
fix(polynomials): avoid out-of-bounds intermediate pointer in token-indexed accessors

The token-indexed proxies and operator[] overloads formed `data() - start_index() + base`
(and `gather/scatter(data() - start_index(), idx)`). When start_index > 0 the intermediate
`data() - start_index()` points before the backing array, which is UB per [expr.add]/4 even
though the final address lands back in-bounds. Rewrite the contiguous paths as
`data() + (base - start_index())` (integer subtraction first) and the gather/scatter paths to
pass `data()` with indices rebased by start_index (new rebase_lane_indices helper), keeping every
in-flight pointer inside the array.

## Patch
### barretenberg/cpp/src/barretenberg/polynomials/polynomial.hpp
```diff
@@ -26,6 +26,19 @@
 #include <vector>
 namespace bb {
 
+// Rebase absolute polynomial indices into offsets relative to data(), so a gather/scatter base
+// pointer stays in-bounds. Forming `data() - start_index()` directly is UB ([expr.add]/4): that
+// intermediate pointer lands before the backing array, even though `base[idx]` later lands inside it.
+template <size_t N>
+[[gnu::always_inline]] inline std::array<size_t, N> rebase_lane_indices(std::array<size_t, N> idx,
+                                                                        size_t start_index) noexcept
+{
+    for (size_t lane = 0; lane < N; ++lane) {
+        idx[lane] -= start_index;
+    }
+    return idx;
+}
+
 /* Span class with a start index offset.
  * We conceptually have a span like a_0 + a_1 x ... a_n x^n and then multiply by x^start_index.
  * This allows more efficient representation than a fully defined span for 'islands' of zeroes. */
@@ -62,7 +75,8 @@ template <typename Fr> struct PolynomialSpan {
     template <size_t N, typename U = element_type> VectorField<typename U::Params> operator[](VectorIndex<N> ctx) const
     {
         static_assert(N == VECTOR_FIELD_WIDTH, "VectorField is fixed-width; N must equal VECTOR_FIELD_WIDTH");
-        return VectorField<typename U::Params>::gather(this->span.data() - this->start_index, ctx.idx);
+        return VectorField<typename U::Params>::gather(this->span.data(),
+                                                       rebase_lane_indices(ctx.idx, this->start_index));
     }
 
     // Contiguous vector read: lane L = this->span[base - start_index + L].
@@ -74,7 +88,7 @@ template <typename Fr> struct PolynomialSpan {
     [[gnu::always_inline]] VectorField<typename U::Params> operator[](ContiguousVectorIndex<N> ctx) const
     {
         static_assert(N == VECTOR_FIELD_WIDTH, "VectorField is fixed-width; N must equal VECTOR_FIELD_WIDTH");
-        return VectorField<typename U::Params>(this->span.data() - this->start_index + ctx.base);
+        return VectorField<typename U::Params>(this->span.data() + (ctx.base - this->start_index));
     }
 
     PolynomialSpan subspan(size_t offset, size_t length)
@@ -471,12 +485,12 @@ template <typename Fr> class Polynomial {
         std::array<size_t, 5> idx;
         [[gnu::always_inline]] VectorWriteProxyT& operator=(const VectorField<Params_>& v)
         {
-            v.scatter(self->data() - self->start_index(), idx);
+            v.scatter(self->data(), rebase_lane_indices(idx, self->start_index()));
             return *this;
         }
         [[gnu::always_inline]] operator VectorField<Params_>() const
         {
-            return VectorField<Params_>::gather(self->data() - self->start_index(), idx);
+            return VectorField<Params_>::gather(self->data(), rebase_lane_indices(idx, self->start_index()));
         }
 
         BB_VECTOR_PROXY_BINARY_OPS(VectorWriteProxyT, VectorField<Params_>, Fr)
@@ -493,12 +507,12 @@ template <typename Fr> class Polynomial {
         size_t base;
         [[gnu::always_inline]] ContiguousVectorWriteProxyT& operator=(const VectorField<Params_>& v)
         {
-            v.store_to(self->data() - self->start_index() + base);
+            v.store_to(self->data() + (base - self->start_index()));
             return *this;
         }
         [[gnu::always_inline]] operator VectorField<Params_>() const
         {
-            return VectorField<Params_>(self->data() - self->start_index() + base);
+            return VectorField<Params_>(self->data() + (base - self->start_index()));
         }
 
         BB_VECTOR_PROXY_BINARY_OPS(ContiguousVectorWriteProxyT, VectorField<Params_>, Fr)
@@ -514,7 +528,7 @@ template <typename Fr> class Polynomial {
     template <size_t N, typename U = Fr> VectorField<typename U::Params> operator[](VectorIndex<N> ctx) const
     {
         static_assert(N == VECTOR_FIELD_WIDTH, "VectorField is fixed-width; N must equal VECTOR_FIELD_WIDTH");
-        return VectorField<typename U::Params>::gather(this->data() - this->start_index(), ctx.idx);
+        return VectorField<typename U::Params>::gather(this->data(), rebase_lane_indices(ctx.idx, this->start_index()));
     }
 
     // Contiguous vector read via token: lane L = (*this)[ctx.base + L].
@@ -523,7 +537,7 @@ template <typename Fr> class Polynomial {
     [[gnu::always_inline]] VectorField<typename U::Params> operator[](ContiguousVectorIndex<N> ctx) const
     {
         static_assert(N == VECTOR_FIELD_WIDTH, "VectorField is fixed-width; N must equal VECTOR_FIELD_WIDTH");
-        return VectorField<typename U::Params>(this->data() - this->start_index() + ctx.base);
+        return VectorField<typename U::Params>(this->data() + (ctx.base - this->start_index()));
     }
 
     // Non-const LHS overloads return write-proxies.
```
