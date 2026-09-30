# [?] fix(pnpm): Patch `immutable`, `svgo` and `multer` vulnerabilities (#10637)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-03-06
Source: https://github.com/iotaledger/iota/commit/0142ab554b9f70eaf6d962260c17432858b49ae7
Type: security-commit

## Details
fix(pnpm): Patch `immutable`, `svgo` and `multer` vulnerabilities (#10637)

Fixes
https://github.com/iotaledger/iota/actions/runs/22737081319/job/65941164904

## Patch
### .changeset/lovely-hairs-travel.md
```diff
@@ -0,0 +1,5 @@
+---
+'@iota/apps-ui-icons': patch
+---
+
+Update svgo dependency.
```

### apps/ui-icons/package.json
```diff
@@ -20,8 +20,8 @@
         "lint:fix": "pnpm run eslint:fix && pnpm run prettier:fix"
     },
     "devDependencies": {
-        "@svgr/cli": "^7.0.0",
-        "@svgr/core": "^7.0.0",
+        "@svgr/cli": "^8.1.0",
+        "@svgr/core": "^8.1.0",
         "@types/react": "^18.3.3",
         "react": "^18.3.1",
         "rimraf": "^5.0.1",
```

### apps/ui-icons/src/Activity.tsx
```diff
@@ -1,7 +1,7 @@
-// Copyright (c) 2025 IOTA Stiftung
+// Copyright (c) 2026 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
 
-import { SVGProps } from 'react';
+import type { SVGProps } from 'react';
 export default function SvgActivity(props: SVGProps<SVGSVGElement>) {
     return (
         <svg
```

### apps/ui-icons/src/Add.tsx
```diff
@@ -1,7 +1,7 @@
-// Copyright (c) 2025 IOTA Stiftung
+// Copyright (c) 2026 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
 
-import { SVGProps } from 'react';
+import type { SVGProps } from 'react';
 export default function SvgAdd(props: SVGProps<SVGSVGElement>) {
     return (
         <svg
```

### apps/ui-icons/src/Apps.tsx
```diff
@@ -1,7 +1,7 @@
-// Copyright (c) 2025 IOTA Stiftung
+// Copyright (c) 2026 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
 
-import { SVGProps } from 'react';
+import type { SVGProps } from 'react';
 export default function SvgApps(props: SVGProps<SVGSVGElement>) {
     return (
         <svg
```

### apps/ui-icons/src/ArrowBack.tsx
```diff
@@ -1,7 +1,7 @@
-// Copyright (c) 2025 IOTA Stiftung
+// Copyright (c) 2026 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
 
-import { SVGProps } from 'react';
+import type { SVGProps } from 'react';
 export default function SvgArrowBack(props: SVGProps<SVGSVGElement>) {
     return (
         <svg
```

### apps/ui-icons/src/ArrowBottomLeft.tsx
```diff
@@ -1,7 +1,7 @@
-// Copyright (c) 2025 IOTA Stiftung
+// Copyright (c) 2026 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
 
-import { SVGProps } from 'react';
+import type { SVGProps } from 'react';
 export default function SvgArrowBottomLeft(props: SVGProps<SVGSVGElement>) {
     return (
         <svg
```

### apps/ui-icons/src/ArrowDown.tsx
```diff
@@ -1,7 +1,7 @@
-// Copyright (c) 2025 IOTA Stiftung
+// Copyright (c) 2026 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
 
-import { SVGProps } from 'react';
+import type { SVGProps } from 'react';
 export default function SvgArrowDown(props: SVGProps<SVGSVGElement>) {
     return (
         <svg
```

### apps/ui-icons/src/ArrowForward.tsx
```diff
@@ -1,7 +1,7 @@
-// Copyright (c) 2025 IOTA Stiftung
+// Copyright (c) 2026 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
 
-import { SVGProps } from 'react';
+import type { SVGProps } from 'react';
 export default function SvgArrowForward(props: SVGProps<SVGSVGElement>) {
     return (
         <svg
```

### apps/ui-icons/src/ArrowLeft.tsx
```diff
@@ -1,7 +1,7 @@
-// Copyright (c) 2025 IOTA Stiftung
+// Copyright (c) 2026 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
 
-import { SVGProps } from 'react';
+import type { SVGProps } from 'react';
 export default function SvgArrowLeft(props: SVGProps<SVGSVGElement>) {
     return (
         <svg
```

### apps/ui-icons/src/ArrowRight.tsx
```diff
@@ -1,7 +1,7 @@
-// Copyright (c) 2025 IOTA Stiftung
+// Copyright (c) 2026 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
 
-import { SVGProps } from 'react';
+import type { SVGProps } from 'react';
 export default function SvgArrowRight(props: SVGProps<SVGSVGElement>) {
     return (
         <svg
```

### apps/ui-icons/src/ArrowTopRight.tsx
```diff
@@ -1,7 +1,7 @@
-// Copyright (c) 2025 IOTA Stiftung
+// Copyright (c) 2026 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
 
-import { SVGProps } from 'react';
+import type { SVGProps } from 'react';
 export default function SvgArrowTopRight(props: SVGProps<SVGSVGElement>) {
     return (
         <svg
```
