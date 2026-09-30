# [?] :bug: Fixed the overflow-scroll interaction on mobile

## Summary
Severity: Unknown
Chain: Oracle
Component: bandprotocol/bandchain
Published: 2020-07-31
Source: https://github.com/bandprotocol/bandchain/commit/5c7e7c2df9ed25a23cf4850611c22b908d650778
Type: security-commit

## Details
:bug: Fixed the overflow-scroll interaction on mobile

## Patch
### scan/src/reusable/Tab.re
```diff
@@ -13,7 +13,7 @@ module Styles = {
       padding2(~v=`zero, ~h=`px(20)),
       borderBottom(`px(1), `solid, Colors.gray4),
       boxShadow(Shadow.box(~x=`zero, ~y=`px(2), ~blur=`px(10), Css.rgba(0, 0, 0, 0.08))),
-      Media.mobile([overflow(`auto)]),
+      Media.mobile([overflow(`auto), padding2(~v=`px(5), ~h=`px(10))]),
     ]);
 
   let buttonContainer = active =>
@@ -26,7 +26,7 @@ module Styles = {
       padding2(~v=Spacing.md, ~h=`px(20)),
       borderBottom(`pxFloat(1.5), `solid, active ? Colors.bandBlue : Colors.white),
       textShadow(Shadow.text(~blur=`pxFloat(active ? 1. : 0.), Colors.bandBlue)),
-      Media.mobile([whiteSpace(`nowrap)]),
+      Media.mobile([whiteSpace(`nowrap), borderColor(Colors.white)]),
     ]);
 
   let childrenContainer =
```
