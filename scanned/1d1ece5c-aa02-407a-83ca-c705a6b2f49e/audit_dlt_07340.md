# [?] fix: yaml resource exhaustion (#5127)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2025-01-08
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/cd7c41308ef982e17cb8ea280e19bf025837a113
Type: security-commit

## Details
fix: yaml resource exhaustion (#5127)

### Description

Fixes 
```
ReferenceError: Excessive alias count indicates a resource exhaustion attack
```

See
https://stackoverflow.com/questions/63075256/why-does-the-npm-yaml-library-have-a-max-alias-number

### Backward compatibility

Yes

### Testing

Manual

## Patch
### .changeset/shaggy-dolphins-wink.md
```diff
@@ -0,0 +1,5 @@
+---
+"@hyperlane-xyz/cli": patch
+---
+
+Fix yaml resource exhaustion
```

### typescript/cli/src/utils/files.ts
```diff
@@ -4,16 +4,26 @@ import fs from 'fs';
 import os from 'os';
 import path from 'path';
 import {
+  DocumentOptions,
   LineCounter,
+  ParseOptions,
+  SchemaOptions,
+  ToJSOptions,
   parse,
-  parse as yamlParse,
   stringify as yamlStringify,
 } from 'yaml';
 
 import { objMerge } from '@hyperlane-xyz/utils';
 
 import { log } from '../logger.js';
 
+const yamlParse = (
+  content: string,
+  options?: ParseOptions & DocumentOptions & SchemaOptions & ToJSOptions,
+) =>
+  // See stackoverflow.com/questions/63075256/why-does-the-npm-yaml-library-have-a-max-alias-number
+  parse(content, { maxAliasCount: -1, ...options });
+
 export const MAX_READ_LINE_OUTPUT = 250;
 
 export type FileFormat = 'yaml' | 'json';
@@ -250,7 +260,7 @@ export function logYamlIfUnderMaxLines(
 ): void {
   const asYamlString = yamlStringify(obj, null, margin);
   const lineCounter = new LineCounter();
-  parse(asYamlString, { lineCounter });
+  yamlParse(asYamlString, { lineCounter });
 
   log(lineCounter.lineStarts.length < maxLines ? asYamlString : '');
 }
```
