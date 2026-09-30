# [?] Fix Checkpoints fuzz overflow (#4184)

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2023-04-25
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/8f14d52b7366eb8dcdbf40a92b2d1cb14ded9a13
Type: security-commit

## Details
Fix Checkpoints fuzz overflow (#4184)

Co-authored-by: Francisco <fg@frang.io>

## Patch
### scripts/generate/templates/Checkpoints.t.js
```diff
@@ -86,10 +86,12 @@ function testPush(
 
     if (keys.length > 0) {
         ${opts.keyTypeName} lastKey = keys[keys.length - 1];
-        pastKey = _bound${capitalize(opts.keyTypeName)}(pastKey, 0, lastKey - 1);
-
-        vm.expectRevert();
-        this.push(pastKey, values[keys.length % values.length]);
+        if (lastKey > 0) {
+            pastKey = _bound${capitalize(opts.keyTypeName)}(pastKey, 0, lastKey - 1);
+    
+            vm.expectRevert();
+            this.push(pastKey, values[keys.length % values.length]);
+        }
     }
 }
 
@@ -173,11 +175,13 @@ function testPush(
     // Can't push any key in the past
     if (keys.length > 0) {
         ${opts.keyTypeName} lastKey = keys[keys.length - 1];
-        pastKey = _bound${capitalize(opts.keyTypeName)}(pastKey, 0, lastKey - 1);
-
-        vm.roll(pastKey);
-        vm.expectRevert();
-        this.push(values[keys.length % values.length]);
+        if (lastKey > 0) {
+            pastKey = _bound${capitalize(opts.keyTypeName)}(pastKey, 0, lastKey - 1);
+    
+            vm.roll(pastKey);
+            vm.expectRevert();
+            this.push(values[keys.length % values.length]);
+        }
     }
 }
 
```

### test/utils/Checkpoints.t.sol
```diff
@@ -66,11 +66,13 @@ contract CheckpointsHistoryTest is Test {
         // Can't push any key in the past
         if (keys.length > 0) {
             uint32 lastKey = keys[keys.length - 1];
-            pastKey = _boundUint32(pastKey, 0, lastKey - 1);
+            if (lastKey > 0) {
+                pastKey = _boundUint32(pastKey, 0, lastKey - 1);
 
-            vm.roll(pastKey);
-            vm.expectRevert();
-            this.push(values[keys.length % values.length]);
+                vm.roll(pastKey);
+                vm.expectRevert();
+                this.push(values[keys.length % values.length]);
+            }
         }
     }
 
@@ -185,10 +187,12 @@ contract CheckpointsTrace224Test is Test {
 
         if (keys.length > 0) {
             uint32 lastKey = keys[keys.length - 1];
-            pastKey = _boundUint32(pastKey, 0, lastKey - 1);
+            if (lastKey > 0) {
+                pastKey = _boundUint32(pastKey, 0, lastKey - 1);
 
-            vm.expectRevert();
-            this.push(pastKey, values[keys.length % values.length]);
+                vm.expectRevert();
+                this.push(pastKey, values[keys.length % values.length]);
+            }
         }
     }
 
@@ -291,10 +295,12 @@ contract CheckpointsTrace160Test is Test {
 
         if (keys.length > 0) {
             uint96 lastKey = keys[keys.length - 1];
-            pastKey = _boundUint96(pastKey, 0, lastKey - 1);
+            if (lastKey > 0) {
+                pastKey = _boundUint96(pastKey, 0, lastKey - 1);
 
-            vm.expectRevert();
-            this.push(pastKey, values[keys.length % values.length]);
+                vm.expectRevert();
+                this.push(pastKey, values[keys.length % values.length]);
+            }
         }
     }
 
```
