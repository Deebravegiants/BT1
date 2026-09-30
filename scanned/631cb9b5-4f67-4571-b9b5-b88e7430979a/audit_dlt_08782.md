# [?] fix: MODEXP_lead_log OOB instruction tracing (#1806)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2025-02-13
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/44f13d45889007851132713679a879db8462331e
Type: security-commit

## Details
fix: MODEXP_lead_log OOB instruction tracing (#1806)

This fix was originally done on a PRC testing branch. Extracted for the
upcoming release.

## Patch
### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/hub/fragment/imc/oob/precompiles/ModexpLeadOobCall.java
```diff
@@ -52,9 +52,9 @@ public net.consensys.linea.zktracer.module.oob.Trace trace(
         .data3(bigIntegerToBytes(ebs))
         .data4(booleanToBytes(loadLead))
         .data5(ZERO)
-        .data6(Bytes.of(cdsCutoff))
-        .data7(Bytes.of(ebsCutoff))
-        .data8(Bytes.of(subEbs32))
+        .data6(Bytes.ofUnsignedInt(cdsCutoff))
+        .data7(Bytes.ofUnsignedInt(ebsCutoff))
+        .data8(Bytes.ofUnsignedInt(subEbs32))
         .data9(ZERO);
   }
 
@@ -68,9 +68,9 @@ public Trace trace(Trace trace) {
         .pMiscOobData3(bigIntegerToBytes(ebs))
         .pMiscOobData4(booleanToBytes(loadLead))
         .pMiscOobData5(ZERO)
-        .pMiscOobData6(Bytes.of(cdsCutoff))
-        .pMiscOobData7(Bytes.of(ebsCutoff))
-        .pMiscOobData8(Bytes.of(subEbs32))
+        .pMiscOobData6(Bytes.ofUnsignedInt(cdsCutoff))
+        .pMiscOobData7(Bytes.ofUnsignedInt(ebsCutoff))
+        .pMiscOobData8(Bytes.ofUnsignedInt(subEbs32))
         .pMiscOobData9(ZERO);
   }
 }
```
