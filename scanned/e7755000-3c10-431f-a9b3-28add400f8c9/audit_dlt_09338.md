# [?] Fixed call stack overflow in makeError stringify for recursive structures (#4977, #4978).

## Summary
Severity: Unknown
Chain: Tooling
Component: ethers-io/ethers.js
Published: 2025-05-26
Source: https://github.com/ethers-io/ethers.js/commit/52a052210919a35b0b0b38e357b3003ac8259fce
Type: security-commit

## Details
Fixed call stack overflow in makeError stringify for recursive structures (#4977, #4978).

## Patch
### src.ts/utils/errors.ts
```diff
@@ -25,11 +25,17 @@ import type { FetchRequest, FetchResponse } from "./fetch.js";
 export type ErrorInfo<T> = Omit<T, "code" | "name" | "message" | "shortMessage"> & { shortMessage?: string };
 
 
-function stringify(value: any): any {
+function stringify(value: any, seen?: Set<any>): any {
     if (value == null) { return "null"; }
 
+    if (seen == null) { seen = new Set(); }
+    if (typeof(value) === "object") {
+        if (seen.has(value)) { return "[Circular]"; }
+        seen.add(value);
+    }
+
     if (Array.isArray(value)) {
-        return "[ " + (value.map(stringify)).join(", ") + " ]";
+        return "[ " + (value.map((v) => stringify(v, seen))).join(", ") + " ]";
     }
 
     if (value instanceof Uint8Array) {
@@ -43,22 +49,20 @@ function stringify(value: any): any {
     }
 
     if (typeof(value) === "object" && typeof(value.toJSON) === "function") {
-        return stringify(value.toJSON());
+        return stringify(value.toJSON(), seen);
     }
 
     switch (typeof(value)) {
-        case "boolean": case "symbol":
+        case "boolean": case "number": case "symbol":
             return value.toString();
         case "bigint":
             return BigInt(value).toString();
-        case "number":
-            return (value).toString();
         case "string":
             return JSON.stringify(value);
         case "object": {
             const keys = Object.keys(value);
             keys.sort();
-            return "{ " + keys.map((k) => `${ stringify(k) }: ${ stringify(value[k]) }`).join(", ") + " }";
+            return "{ " + keys.map((k) => `${ stringify(k, seen) }: ${ stringify(value[k], seen) }`).join(", ") + " }";
         }
     }
 
```
