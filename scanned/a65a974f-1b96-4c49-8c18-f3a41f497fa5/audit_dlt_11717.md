# [?] fix scriptsig asm parsing buffer overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2025-12-10
Source: https://github.com/mempool/mempool/commit/fcbdf7e71d786283f1fc4b6b3b3733da57114cf5
Type: security-commit

## Details
fix scriptsig asm parsing buffer overflow

## Patch
### backend/src/api/transaction-utils.ts
```diff
@@ -300,15 +300,15 @@ class TransactionUtils {
       if (op >= 0x01 && op <= 0x4e) {
         i++;
         let push: number;
-        if (op === 0x4c) {
+        if (op === 0x4c && buf.length > i) {
           push = buf.readUInt8(i);
           b.push('OP_PUSHDATA1');
           i += 1;
-        } else if (op === 0x4d) {
+        } else if (op === 0x4d && buf.length > i + 1) {
           push = buf.readUInt16LE(i);
           b.push('OP_PUSHDATA2');
           i += 2;
-        } else if (op === 0x4e) {
+        } else if (op === 0x4e && buf.length > i + 3) {
           push = buf.readUInt32LE(i);
           b.push('OP_PUSHDATA4');
           i += 4;
@@ -317,13 +317,15 @@ class TransactionUtils {
           b.push('OP_PUSHBYTES_' + push);
         }
 
-        const data = buf.slice(i, i + push);
-        if (data.length !== push) {
+        if (i >= buf.length) {
           break;
         }
-
+        const data = buf.subarray(i, Math.min(i + push, buf.length));
         b.push(data.toString('hex'));
         i += data.length;
+        if (data.length !== push) {
+          break;
+        }
       } else {
         if (op === 0x00) {
           b.push('OP_0');
```
