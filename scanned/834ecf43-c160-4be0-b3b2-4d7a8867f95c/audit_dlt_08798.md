# [?] fix: update besu to 24.4-develop-a5a3eb8 and disable OOB, BLAKE2f_MODEXP_DATA and EXP modules (#738)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2024-05-29
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/ae5e59c1d14929795a69b64ceae8045616c0d8ef
Type: security-commit

## Details
fix: update besu to 24.4-develop-a5a3eb8 and disable OOB, BLAKE2f_MODEXP_DATA and EXP modules (#738)

Resolves: #715 

Signed-off-by: Tsvetan Dimitrov <tsvetan.dimitrov@consensys.net>

## Patch
### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/hub/Hub.java
```diff
@@ -340,7 +340,8 @@ public List<Module> getModulesToTrace() {
                 this,
                 this.add,
                 this.bin,
-                this.blake2fModexpData,
+                // WARNING: Temporarily disabled.
+                //                this.blake2fModexpData,
                 this.ecData,
                 this.blockdata,
                 this.blockhash,
@@ -354,7 +355,8 @@ public List<Module> getModulesToTrace() {
                 this.mod,
                 this.mul,
                 this.mxp,
-                this.oob,
+                // WARNING: Temporarily disabled.
+                //                this.oob,
                 this.rlpAddr,
                 this.rlpTxn,
                 this.rlpTxrcpt,
@@ -394,7 +396,8 @@ public List<Module> getModulesToCount() {
                 this.mod,
                 this.mul,
                 this.mxp,
-                this.oob,
+                // WARNING: Temporarily disabled.
+                //                this.oob,
                 this.exp,
                 this.rlpAddr,
                 this.rlpTxn,
```

### tracer/zkevm-constraints
```diff
@@ -1 +1 @@
-Subproject commit 89a03455611d41cb4c1b292c0931e0edf65012a8
+Subproject commit 74923d612fe978b9905daacfe064c9a286306e7c
```
