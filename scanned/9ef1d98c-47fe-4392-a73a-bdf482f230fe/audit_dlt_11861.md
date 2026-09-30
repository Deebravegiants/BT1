# [?] Fix panic on null exn passed to error handling (#203)

## Summary
Severity: Unknown
Chain: Indexer
Component: enviodev/hyperindex
Published: 2024-09-16
Source: https://github.com/enviodev/hyperindex/commit/125b21776d9a56bf5a25788bd333681bf599cb3d
Type: security-commit

## Details
Fix panic on null exn passed to error handling (#203)

## Patch
### codegenerator/cli/templates/static/codegen/src/ErrorHandling.res
```diff
@@ -3,11 +3,16 @@ type exnType = Js(Js.Exn.t) | Other(exn)
 type t = {logger: Pino.t, exn: exnType, msg: option<string>}
 
 let makeExnType = (exn): exnType => {
-  switch exn {
-  | Js.Exn.Error(e)
-  | Promise.JsError(e) =>
-    Js(e)
-  | exn => Other(exn)
+  // exn might be not an object which will break the pattern match by RE_EXN_ID
+  if exn->Obj.magic {
+    switch exn {
+    | Js.Exn.Error(e)
+    | Promise.JsError(e) =>
+      Js(e)
+    | exn => Other(exn)
+    }
+  } else {
+    Other(exn)
   }
 }
 
```
