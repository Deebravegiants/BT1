# [?] constrain q, d in amount division to guard against overflow

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-08-12
Source: https://github.com/penumbra-zone/penumbra/commit/a19ca906552dca7a48414c08cd269ddf00ca21b3
Type: security-commit

## Details
constrain q, d in amount division to guard against overflow

## Patch
### crates/core/num/src/amount.rs
```diff
@@ -1,6 +1,6 @@
-use ark_ff::ToConstraintField;
+use ark_ff::{BigInteger, PrimeField, ToConstraintField};
 use ark_r1cs_std::{prelude::*, uint64::UInt64};
-use ark_relations::r1cs::SynthesisError;
+use ark_relations::r1cs::{ConstraintSystemRef, SynthesisError};
 use decaf377::{Fq, Fr};
 use penumbra_proto::{core::crypto::v1alpha1 as pb, DomainType, TypeUrl};
 use serde::{Deserialize, Serialize};
@@ -83,6 +83,31 @@ impl ToConstraintField<Fq> for Amount {
     }
 }
 
+/// Return a boolean constraint indicating if the FqVar can be represented using n bits
+pub fn is_bit_constrained(
+    cs: ConstraintSystemRef<Fq>,
+    value: FqVar,
+    n: usize,
+) -> Result<Boolean<Fq>, SynthesisError> {
+    let inner = value.value().unwrap_or(Fq::from(1u64));
+
+    // Get only first n bits based on that value (OOC)
+    let inner_bigint = inner.into_bigint();
+    let bits = &inner_bigint.to_bits_le()[0..n];
+
+    // Allocate Boolean vars for first n bits
+    let mut boolean_constraints = Vec::new();
+    for bit in bits {
+        let boolean = Boolean::new_witness(cs.clone(), || Ok(bit))?;
+        boolean_constraints.push(boolean);
+    }
+
+    // Construct an FqVar from those n Boolean constraints
+    let constructed_fqvar = Boolean::<Fq>::le_bits_to_fp_var(&boolean_constraints.to_bits_le()?)
+        .expect("can convert to bits");
+    constructed_fqvar.is_eq(&value)
+}
+
 impl AmountVar {
     pub fn negate(&self) -> Result<Self, SynthesisError> {
         Ok(Self {
@@ -113,6 +138,12 @@ impl AmountVar {
         let quo_var = AmountVar::new_witness(self.cs(), || Ok(Fq::from(quo)))?;
         let rem_var = AmountVar::new_witness(self.cs(), || Ok(Fq::from(rem)))?;
 
+        // Constrain either quo_var or divisior_var to be 64 bits to guard against overflow
+        let q_is_64_bits = is_bit_constrained(self.cs(), quo_var.amount.clone(), 64)?;
+        let d_is_64_bits = is_bit_constrained(self.cs(), divisor_var.amount.clone(), 64)?;
+        let q_or_d_is_64_bits = q_is_64_bits.or(&d_is_64_bits)?;
+        q_or_d_is_64_bits.enforce_equal(&Boolean::constant(true))?;
+
         // Constrain: numerator = quo * divisor + rem
         let numerator_var = quo_var.clone() * divisor_var.clone() + rem_var.clone();
         self.enforce_equal(&numerator_var)?;
```
