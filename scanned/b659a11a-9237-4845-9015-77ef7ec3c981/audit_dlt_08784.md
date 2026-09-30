# [?] Fixing `underflowException` in `KeccakSection` (#1401)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2024-10-09
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/89cbf0d921c0949e3a3feab113c997a07e717520
Type: security-commit

## Details
Fixing `underflowException` in `KeccakSection` (#1401)

## Patch
### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/blockhash/Blockhash.java
```diff
@@ -105,6 +105,7 @@ public void tracePreOpcode(MessageFrame frame) {
   @Override
   public void resolvePostExecution(
       Hub hub, MessageFrame frame, Operation.OperationResult operationResult) {
+
     final OpCode opCode = OpCode.of(frame.getCurrentOperation().getOpcode());
     if (opCode == OpCode.BLOCKHASH) {
       final Bytes32 result = Bytes32.leftPad(frame.getStackItem(0));
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/hub/section/KeccakSection.java
```diff
@@ -60,6 +60,11 @@ public KeccakSection(Hub hub) {
   @Override
   public void resolvePostExecution(
       Hub hub, MessageFrame frame, Operation.OperationResult operationResult) {
+
+    if (Exceptions.any(hub.pch().exceptions())) {
+      return;
+    }
+
     final Bytes32 hashResult = Bytes32.leftPad(frame.getStackItem(0));
 
     // retroactively set HASH_INFO_FLAG and HASH_INFO_KECCAK_HI, HASH_INFO_KECCAK_LO
```
