# [?] fix(website): hero overflow-right taikogeom (#443)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2022-12-15
Source: https://github.com/taikoxyz/taiko-mono/commit/2fa40e0491ed0c16c1d87834fa79aa21fe09d187
Type: security-commit

## Details
fix(website): hero overflow-right taikogeom (#443)

## Patch
### packages/website/src/components/Hero/index.tsx
```diff
@@ -59,11 +59,11 @@ export default function Hero() {
 
         <div
           id="taikoGeomParent"
-          className="absolute inset-y-0 -right-6 overflow-hidden h-full w-11/12 lg:absolute lg:inset-y-0 lg:right-0 lg:h-full lg:w-1/2"
+          className="absolute inset-y-0 right-0 overflow-hidden h-full w-11/12 lg:absolute lg:inset-y-0 lg:right-0 lg:h-full lg:w-1/2"
         >
           <img
             id="taikoGeom"
-            className="absolute z-0 overflow-visible h-full w-full object-cover max-w-none"
+            className="absolute z-0 -right-6 overflow-visible h-full w-full object-cover max-w-none"
             src="./img/Taiko_GEOM_1_Fluo_Sliced.svg"
             alt=""
           />
```
