# [?] Convert router liquidity to BN to prevent overflow

## Summary
Severity: Unknown
Chain: Connext
Component: connext/monorepo
Published: 2023-03-01
Source: https://github.com/connext/monorepo/commit/479065314e3b7cf6d32212a830baf044df350372
Type: security-commit

## Details
Convert router liquidity to BN to prevent overflow

## Patch
### packages/agents/sdk/src/sdkUtils.ts
```diff
@@ -1,4 +1,4 @@
-import { utils } from "ethers";
+import { utils, BigNumber } from "ethers";
 import {
   Logger,
   ChainData,
@@ -249,7 +249,7 @@ export class SdkUtils extends SdkShared {
    * @returns The total router liquidity available for the asset.
    *
    */
-  async checkRouterLiquidity(domainId: string, asset: string, topN?: number) {
+  async checkRouterLiquidity(domainId: string, asset: string, topN?: number): Promise<BigNumber> {
     const _asset = utils.getAddress(asset);
     const _topN = topN ?? 4;
 
@@ -260,6 +260,8 @@ export class SdkUtils extends SdkShared {
         routerBalance.domain == domainId && utils.getAddress(routerBalance.local) == _asset,
     );
 
-    return eligibleRouters.slice(0, _topN).reduce((acc, router) => acc + router.balance, 0);
+    return eligibleRouters
+      .slice(0, _topN)
+      .reduce((acc, router) => acc.add(BigNumber.from(router.balance.toString())), BigNumber.from(0));
   }
 }
```
