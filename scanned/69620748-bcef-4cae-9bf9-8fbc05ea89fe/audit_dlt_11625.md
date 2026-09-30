# [?] fix(ci): Race condition in wait-for-follower script (#11159)

## Summary
Severity: Unknown
Chain: Agoric
Component: Agoric/agoric-sdk
Published: 2025-03-27
Source: https://github.com/Agoric/agoric-sdk/commit/0e80151700ff31478ebb29b4767e87839cbcc66c
Type: security-commit

## Details
fix(ci): Race condition in wait-for-follower script (#11159)

closes: https://github.com/Agoric/product-tasks/issues/264
refs: #XXXX

## Description
Due to a possible race condition in the [wait-for-follower.mjs](https://github.com/Agoric/agoric-sdk/blob/master/a3p-integration/proposals/z%3Aacceptance/wait-for-follower.mjs) script, the CI job can hang. The script first checks for the current contents of the file and then starts a watcher on the file. If the intended message was written to the file in between, the script never exits and the CI job hangs.
This PR adds a wrapper on the file watcher and reports a fake event first to check the existing file contents before starting the actual file watcher

### Security Considerations
None

### Scaling Considerations
None

### Documentation Considerations
None

### Testing Considerations
CI build should pass

### Upgrade Considerations
None

## Patch
### a3p-integration/proposals/z:acceptance/wait-for-follower.mjs
```diff
@@ -1,6 +1,6 @@
 /* eslint-env node */
 
-import { readFile, watch } from 'fs/promises';
+import { watch, readFileSync } from 'fs';
 
 const FILE_ENCODING = 'utf-8';
 const FILE_PATH = process.env.MESSAGE_FILE_PATH;
@@ -9,29 +9,55 @@ const FILE_PATH = process.env.MESSAGE_FILE_PATH;
  * @param {string} filePath
  * @param {string} message
  */
-const checkFileContent = async (filePath, message) => {
-  const fileContent = (await readFile(filePath, FILE_ENCODING)).trim();
+const checkFileContent = (filePath, message) => {
+  const fileContent = readFileSync(filePath, FILE_ENCODING).trim();
   if (!new RegExp(message).test(fileContent)) return '';
   return fileContent;
 };
 
 /**
  * @param {string} filePath
  */
-const watchSharedFile = async filePath => {
+const watchSharedFile = filePath => {
   const [, , message] = process.argv;
 
-  let possibleContent = await checkFileContent(filePath, message);
-  if (possibleContent) return possibleContent;
+  return /** @type {Promise<string>} */ (
+    new Promise((resolve, reject) => {
+      /**
+       * @type {import('fs').FSWatcher}
+       */
+      let watcher;
+      /**
+       * @type {Error}
+       */
+      let error;
 
-  for await (const { eventType } of watch(filePath)) {
-    if (eventType === 'change') {
-      possibleContent = await checkFileContent(filePath, message);
-      if (possibleContent) return possibleContent;
-    }
-  }
+      /**
+       * @param {import('fs').WatchEventType} eventType
+       */
+      const listener = eventType => {
+        try {
+          if (eventType === 'change') {
+            const possibleContent = checkFileContent(filePath, message);
+            if (possibleContent) {
+              watcher.close();
+              resolve(possibleContent);
+            }
+          }
+        } catch (err) {
+          watcher.close();
+          error = err;
+        }
+      };
 
-  return undefined;
+      watcher = watch(filePath, FILE_ENCODING, listener);
+
+      watcher.on('close', () => reject(error ?? Error('Watcher closed')));
+      watcher.on('error', err => reject(err));
+
+      listener('change');
+    })
+  );
 };
 
 FILE_PATH &&
```
