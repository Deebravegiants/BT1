# [?] fix: crash on search token in assets list popup. (#2350)

## Summary
Severity: Unknown
Chain: Rabby
Component: RabbyHub/Rabby
Published: 2024-06-26
Source: https://github.com/RabbyHub/Rabby/commit/2a59da9b62112d5dab0983dd139970df23c3cc3f
Type: security-commit

## Details
fix: crash on search token in assets list popup. (#2350)

## Patch
### src/ui/hooks/useSearchToken.ts
```diff
@@ -13,6 +13,7 @@ import { findChainByServerID } from '@/utils/chain';
 import { Chain } from '@debank/common';
 import useDebounceValue from './useDebounceValue';
 import { useRefState } from './useRefState';
+import { safeBuildRegExp } from '@/utils/string';
 
 function isSearchInputWeb3Address(q: string) {
   return q.length === 42 && q.toLowerCase().startsWith('0x');
@@ -324,7 +325,7 @@ const useSearchToken = (
           list = list.filter((item) => item.amount > 0);
         }
       }
-      const reg = new RegExp(q, 'i');
+      const reg = safeBuildRegExp(q, 'i');
       const matchCustomTokens = customize.filter((token) => {
         return (
           reg.test(token.name) ||
```

### src/ui/views/CommonPopup/AssetList/useFilterProtocolList.ts
```diff
@@ -1,5 +1,6 @@
 import { isSameAddress } from '@/ui/utils';
 import { DisplayedProject } from '@/ui/utils/portfolio/project';
+import { safeBuildRegExp } from '@/utils/string';
 import { useMemo } from 'react';
 
 export const useFilterProtocolList = ({
@@ -20,7 +21,7 @@ export const useFilterProtocolList = ({
             if (kw.length === 42 && kw.toLowerCase().startsWith('0x')) {
               return isSameAddress(token.id, kw);
             } else {
-              const reg = new RegExp(kw, 'i');
+              const reg = safeBuildRegExp(kw, 'i');
               return (
                 reg.test(token.display_symbol || '') || reg.test(token.symbol)
               );
```

### src/utils/string.ts
```diff
@@ -13,3 +13,13 @@ export function unPrefix(str = '', prefix = '/') {
 export function unSuffix(str = '', suffix = '/') {
   return str.endsWith(suffix) ? str.slice(0, -suffix.length) : str;
 }
+
+function escapeRegExp(str: string) {
+  return str.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&');
+}
+
+export function safeBuildRegExp(
+  ...[str, flags]: ConstructorParameters<typeof RegExp>
+) {
+  return new RegExp(str instanceof RegExp ? str : escapeRegExp(str), flags);
+}
```
