# [?] Fix CVE-2019-7167

## Summary
Severity: Unknown
Chain: ZK
Component: iden3/snarkjs
Published: 2019-02-05
Source: https://github.com/iden3/snarkjs/commit/71c66408f5b2316ed2caf4730cc0b79769febad3
Type: security-commit

## Details
Fix CVE-2019-7167

## Patch
### src/setup_original.js
```diff
@@ -189,8 +189,9 @@ function calculateEncriptedValuesAtT(setup, circuit) {
                 }
         */
 
-
-        setup.vk_proof.Ap[s] = G1.affine(G1.mulScalar(A, setup.toxic.ka));
+        if (s > setup.vk_proof.nPublic) {
+            setup.vk_proof.Ap[s] = G1.affine(G1.mulScalar(A, setup.toxic.ka));
+        }
         setup.vk_proof.Bp[s] = G1.affine(G1.mulScalar(B1, setup.toxic.kb));
         setup.vk_proof.Cp[s] = G1.affine(G1.mulScalar(C, setup.toxic.kc));
         setup.vk_proof.Kp[s] = G1.affine(G1.mulScalar(K, setup.toxic.kbeta));
```
