# [?] :bug: Fix sorting function bug, the overflow issue and tab redirection

## Summary
Severity: Unknown
Chain: Oracle
Component: bandprotocol/bandchain
Published: 2020-07-30
Source: https://github.com/bandprotocol/bandchain/commit/87015df427a5e6e2328ea5d5487ce5f164da956f
Type: security-commit

## Details
:bug: Fix sorting function bug, the overflow issue and tab redirection

## Patch
### scan/src/components/ValidatorsTable.re
```diff
@@ -293,8 +293,8 @@ let sorting = (validators: array(ValidatorSub.t), sortedBy) => {
   ->Belt.List.sort((a, b) => {
       let result = {
         switch (sortedBy) {
-        | NameAsc => compareString(a.moniker, b.moniker)
-        | NameDesc => compareString(b.moniker, a.moniker)
+        | NameAsc => compareString(b.moniker, a.moniker)
+        | NameDesc => compareString(a.moniker, b.moniker)
         | VotingPowerAsc => compare(a.tokens, b.tokens)
         | VotingPowerDesc => compare(b.tokens, a.tokens)
         | CommissionAsc => compare(a.commission, b.commission)
```

### scan/src/images/Images.re
```diff
@@ -66,12 +66,14 @@
 [@bs.module] external ledgerStep2Cosmos: string = "./ledger-step2-cosmos.svg";
 [@bs.module] external ledgerStep2BandChain: string = "./ledger-step2-bandchain.svg";
 [@bs.module] external sort: string = "./sort.svg";
-[@bs.module] external mobileSort: string = "./mobile-sort-icon.svg";
-[@bs.module] external mobileSortActive: string = "./mobile-sort-icon-active.svg";
 [@bs.module] external triangleDown: string = "./triangle-down.svg";
 [@bs.module] external sortDown: string = "./down-arrow.svg";
 [@bs.module] external closeButton: string = "./closeButton.svg";
 [@bs.module] external whiteCheck: string = "./white-check.svg";
 [@bs.module] external whiteClose: string = "./white-close.svg";
 [@bs.module] external close: string = "./close.svg";
 [@bs.module] external menu: string = "./menu.svg";
+[@bs.module] external mobileSortAsc: string = "./mobile-sort-asc-icon.svg";
+[@bs.module] external mobileSortDesc: string = "./mobile-sort-desc-icon.svg";
+[@bs.module] external mobileSortAscActive: string = "./mobile-sort-asc-active-icon.svg";
+[@bs.module] external mobileSortDescActive: string = "./mobile-sort-desc-active-icon.svg";
```

### scan/src/images/mobile-sort-asc-active-icon.svg
```diff
@@ -1,7 +1,7 @@
 <?xml version="1.0" encoding="UTF-8"?>
 <svg width="26px" height="13px" viewBox="0 0 26 13" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
     <!-- Generator: sketchtool 59.1 (101010) - https://sketch.com -->
-    <title>AE79BC28-AF52-4235-ADB9-E470A9D01896</title>
+    <title>FB8A1189-CED4-4FD1-A7B0-7C586CC12B06</title>
     <desc>Created with sketchtool.</desc>
     <defs>
         <filter x="-8.5%" y="-4.7%" width="116.9%" height="109.4%" filterUnits="objectBoundingBox" id="filter-1">
@@ -15,13 +15,13 @@
         </filter>
     </defs>
     <g id="Mobile-UI" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
-        <g id="Validator-Home---Sort-by" transform="translate(-223.000000, -434.000000)">
+        <g id="Validator-Home---Sort-by" transform="translate(-223.000000, -498.000000)">
             <g id="Group-12" filter="url(#filter-1)" transform="translate(218.000000, 424.000000)">
-                <g id="icon/descending-copy" transform="translate(8.000000, 10.000000)">
+                <g id="icon/descending-copy-3" transform="translate(8.000000, 74.000000)">
                     <g id="Group-12">
                         <rect id="Rectangle" x="0" y="0" width="20" height="12"></rect>
-                        <polygon id="" fill="#142AB8" fill-rule="nonzero" points="0.992 5.8 5 1.792 9.008 5.8 8.276 6.508 5.492 3.712 5.492 9.808 4.508 9.808 4.508 3.712 1.7 6.508"></polygon>
-                        <path d="M10.008,2.536 L18.992,2.536 L18.992,3.544 L10.008,3.544 L10.008,2.536 Z M10.008,5.044 L15.668,5.044 L15.668,6.052 L10.008,6.052 L10.008,5.044 Z M10.008,7.552 L12.334667,7.552 L12.334667,8.536 L10.008,8.536 L10.008,7.552 Z" id="" fill="#333333" fill-rule="nonzero" transform="translate(14.500000, 5.536000) scale(1, -1) translate(-14.500000, -5.536000) "></path>
+                        <polygon id="" fill="#142AB8" fill-rule="nonzero" transform="translate(5.000000, 5.800000) scale(1, -1) translate(-5.000000, -5.800000) " points="0.992 5.8 5 1.792 9.008 5.8 8.276 6.508 5.492 3.712 5.492 9.808 4.508 9.808 4.508 3.712 1.7 6.508"></polygon>
+                        <path d="M10.008,2.536 L18.992,2.536 L18.992,3.544 L10.008,3.544 L10.008,2.536 Z M10.008,5.044 L15.668,5.044 L15.668,6.052 L10.008,6.052 L10.008,5.044 Z M10.008,7.552 L12.334667,7.552 L12.334667,8.536 L10.008,8.536 L10.008,7.552 Z" id="" fill="#142AB8" fill-rule="nonzero" transform="translate(14.500000, 5.536000) scale(1, -1) translate(-14.500000, -5.536000) "></path>
                     </g>
                 </g>
             </g>
```

### scan/src/images/mobile-sort-asc-icon.svg
```diff
@@ -1,7 +1,7 @@
 <?xml version="1.0" encoding="UTF-8"?>
 <svg width="26px" height="13px" viewBox="0 0 26 13" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
     <!-- Generator: sketchtool 59.1 (101010) - https://sketch.com -->
-    <title>AE79BC28-AF52-4235-ADB9-E470A9D01896</title>
+    <title>FB8A1189-CED4-4FD1-A7B0-7C586CC12B06</title>
     <desc>Created with sketchtool.</desc>
     <defs>
         <filter x="-8.5%" y="-4.7%" width="116.9%" height="109.4%" filterUnits="objectBoundingBox" id="filter-1">
@@ -15,12 +15,12 @@
         </filter>
     </defs>
     <g id="Mobile-UI" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
-        <g id="Validator-Home---Sort-by" transform="translate(-223.000000, -434.000000)">
+        <g id="Validator-Home---Sort-by" transform="translate(-223.000000, -498.000000)">
             <g id="Group-12" filter="url(#filter-1)" transform="translate(218.000000, 424.000000)">
-                <g id="icon/descending-copy" transform="translate(8.000000, 10.000000)">
+                <g id="icon/descending-copy-3" transform="translate(8.000000, 74.000000)">
                     <g id="Group-12">
                         <rect id="Rectangle" x="0" y="0" width="20" height="12"></rect>
-                        <polygon id="" fill="#333333" fill-rule="nonzero" points="0.992 5.8 5 1.792 9.008 5.8 8.276 6.508 5.492 3.712 5.492 9.808 4.508 9.808 4.508 3.712 1.7 6.508"></polygon>
+                        <polygon id="" fill="#333333" fill-rule="nonzero" transform="translate(5.000000, 5.800000) scale(1, -1) translate(-5.000000, -5.800000) " points="0.992 5.8 5 1.792 9.008 5.8 8.276 6.508 5.492 3.712 5.492 9.808 4.508 9.808 4.508 3.712 1.7 6.508"></polygon>
                         <path d="M10.008,2.536 L18.992,2.536 L18.992,3.544 L10.008,3.544 L10.008,2.536 Z M10.008,5.044 L15.668,5.044 L15.668,6.052 L10.008,6.052 L10.008,5.044 Z M10.008,7.552 L12.334667,7.552 L12.334667,8.536 L10.008,8.536 L10.008,7.552 Z" id="" fill="#333333" fill-rule="nonzero" transform="translate(14.500000, 5.536000) scale(1, -1) translate(-14.500000, -5.536000) "></path>
                     </g>
                 </g>
```

### scan/src/images/mobile-sort-desc-active-icon.svg
```diff
@@ -0,0 +1,30 @@
+<?xml version="1.0" encoding="UTF-8"?>
+<svg width="26px" height="13px" viewBox="0 0 26 13" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
+    <!-- Generator: sketchtool 59.1 (101010) - https://sketch.com -->
+    <title>73D69E1D-431A-4734-BC8E-E8C3CB1BD4FB</title>
+    <desc>Created with sketchtool.</desc>
+    <defs>
+        <filter x="-8.5%" y="-4.7%" width="116.9%" height="109.4%" filterUnits="objectBoundingBox" id="filter-1">
+            <feOffset dx="0" dy="2" in="SourceAlpha" result="shadowOffsetOuter1"></feOffset>
+            <feGaussianBlur stdDeviation="2" in="shadowOffsetOuter1" result="shadowBlurOuter1"></feGaussianBlur>
+            <feColorMatrix values="0 0 0 0 0   0 0 0 0 0   0 0 0 0 0  0 0 0 0.08 0" type="matrix" in="shadowBlurOuter1" result="shadowMatrixOuter1"></feColorMatrix>
+            <feMerge>
+                <feMergeNode in="shadowMatrixOuter1"></feMergeNode>
+                <feMergeNode in="SourceGraphic"></feMergeNode>
+            </feMerge>
+        </filter>
+    </defs>
+    <g id="Mobile-UI" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
+        <g id="Validator-Home---Sort-by" transform="translate(-223.000000, -466.000000)">
+            <g id="Group-12" filter="url(#filter-1)" transform="translate(218.000000, 424.000000)">
+                <g id="icon/descending-copy-2" transform="translate(8.000000, 42.000000)">
+                    <g id="Group-12-Copy">
+                        <rect id="Rectangle" x="0" y="0" width="20" height="12"></rect>
+                        <polygon id="" fill="#142AB8" fill-rule="nonzero" transform="translate(5.000000, 5.800000) scale(1, -1) translate(-5.000000, -5.800000) " points="0.992 5.8 5 1.792 9.008 5.8 8.276 6.508 5.492 3.712 5.492 9.808 4.508 9.808 4.508 3.712 1.7 6.508"></polygon>
+                        <path d="M10.008,2.536 L18.992,2.536 L18.992,3.544 L10.008,3.544 L10.008,2.536 Z M10.008,5.044 L15.668,5.044 L15.668,6.052 L10.008,6.052 L10.008,5.044 Z M10.008,7.552 L12.334667,7.552 L12.334667,8.536 L10.008,8.536 L10.008,7.552 Z" id="" fill="#142AB8" fill-rule="nonzero"></path>
+                    </g>
+                </g>
+            </g>
+        </g>
+    </g>
+</svg>
\ No newline at end of file
```

### scan/src/images/mobile-sort-desc-icon.svg
```diff
@@ -0,0 +1,30 @@
+<?xml version="1.0" encoding="UTF-8"?>
+<svg width="26px" height="13px" viewBox="0 0 26 13" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
+    <!-- Generator: sketchtool 59.1 (101010) - https://sketch.com -->
+    <title>73D69E1D-431A-4734-BC8E-E8C3CB1BD4FB</title>
+    <desc>Created with sketchtool.</desc>
+    <defs>
+        <filter x="-8.5%" y="-4.7%" width="116.9%" height="109.4%" filterUnits="objectBoundingBox" id="filter-1">
+            <feOffset dx="0" dy="2" in="SourceAlpha" result="shadowOffsetOuter1"></feOffset>
+            <feGaussianBlur stdDeviation="2" in="shadowOffsetOuter1" result="shadowBlurOuter1"></feGaussianBlur>
+            <feColorMatrix values="0 0 0 0 0   0 0 0 0 0   0 0 0 0 0  0 0 0 0.08 0" type="matrix" in="shadowBlurOuter1" result="shadowMatrixOuter1"></feColorMatrix>
+            <feMerge>
+                <feMergeNode in="shadowMatrixOuter1"></feMergeNode>
+                <feMergeNode in="SourceGraphic"></feMergeNode>
+            </feMerge>
+        </filter>
+    </defs>
+    <g id="Mobile-UI" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
+        <g id="Validator-Home---Sort-by" transform="translate(-223.000000, -466.000000)">
+            <g id="Group-12" filter="url(#filter-1)" transform="translate(218.000000, 424.000000)">
+                <g id="icon/descending-copy-2" transform="translate(8.000000, 42.000000)">
+                    <g id="Group-12-Copy">
+                        <rect id="Rectangle" x="0" y="0" width="20" height="12"></rect>
+                        <polygon id="" fill="#333333" fill-rule="nonzero" transform="translate(5.000000, 5.800000) scale(1, -1) translate(-5.000000, -5.800000) " points="0.992 5.8 5 1.792 9.008 5.8 8.276 6.508 5.492 3.712 5.492 9.808 4.508 9.808 4.508 3.712 1.7 6.508"></polygon>
+                        <path d="M10.008,2.536 L18.992,2.536 L18.992,3.544 L10.008,3.544 L10.008,2.536 Z M10.008,5.044 L15.668,5.044 L15.668,6.052 L10.008,6.052 L10.008,5.044 Z M10.008,7.552 L12.334667,7.552 L12.334667,8.536 L10.008,8.536 L10.008,7.552 Z" id="" fill="#333333" fill-rule="nonzero"></path>
+                    </g>
+                </g>
+            </g>
+        </g>
+    </g>
+</svg>
\ No newline at end of file
```

### scan/src/pages/ValidatorHomePage.re
```diff
@@ -121,6 +121,9 @@ module Styles = {
   };
   let sortDropdownTextItem = {
     style([
+      display(`flex),
+      alignItems(`center),
+      justifyContent(`spaceBetween),
       paddingRight(`px(15)),
       after([
         contentRule(`text("")),
@@ -135,20 +138,7 @@ module Styles = {
         right(`zero),
         transform(translateY(`percent(-50.))),
       ]),
-    ]);
-  };
-  let sortImage = direction => {
-    style([
-      transform(
-        scaleY(
-          {
-            switch (direction) {
-            | ValidatorsTable.ASC => 1 |> float_of_int
-            | DESC => (-1) |> float_of_int
-            };
-          },
-        ),
-      ),
+      selector("> img", [marginRight(`px(10))]),
     ]);
   };
 };
@@ -180,6 +170,14 @@ module SortableDropdown = {
     ];
     <div className=Styles.sortDrowdownContainer>
       <div className=Styles.sortDropdownTextItem onClick={_ => setShow(prev => !prev)}>
+        <img
+          src={
+            switch (ValidatorsTable.getDirection(sortedBy)) {
+            | ASC => Images.mobileSortAsc
+            | DESC => Images.mobileSortDesc
+            }
+          }
+        />
         <Text
           block=true
           value={ValidatorsTable.getName(sortedBy)}
@@ -199,10 +197,15 @@ module SortableDropdown = {
                onClick={_ => {
                  setSortedBy(_ => value);
                  setShow(_ => false);
+                 Js.Console.log(value);
                }}>
                <img
-                 src={isActive ? Images.mobileSortActive : Images.mobileSort}
-                 className={Styles.sortImage(ValidatorsTable.getDirection(value))}
+                 src={
+                   switch (ValidatorsTable.getDirection(value)) {
+                   | ASC => isActive ? Images.mobileSortAscActive : Images.mobileSortAsc
+                   | DESC => isActive ? Images.mobileSortDescActive : Images.mobileSortDesc
+                   }
+                 }
                />
                <Text
                  block=true
```

### scan/src/reusable/Link.re
```diff
@@ -5,7 +5,7 @@ module Styles = {
 };
 
 [@react.component]
-let make = (~route, ~className, ~onClick=() => (), ~children) => {
+let make = (~route, ~className, ~onClick=() => (), ~isTab=false, ~children) => {
   <a
     href={route->Route.toString}
     className={Css.merge([Styles.a, className])}
@@ -19,7 +19,7 @@ let make = (~route, ~className, ~onClick=() => (), ~children) => {
         onClick();
         event->ReactEvent.Mouse.preventDefault;
         route->Route.redirect;
-        Window.scrollTo(0, 0);
+        !isTab ? Window.scrollTo(0, 0) : ();
       }
     }>
     children
```

### scan/src/reusable/Tab.re
```diff
@@ -5,7 +5,7 @@ module Styles = {
     style([
       backgroundColor(Colors.white),
       boxShadow(Shadow.box(~x=`zero, ~y=`px(2), ~blur=`px(10), Css.rgba(0, 0, 0, 0.08))),
-      Media.mobile([margin2(~h=`px(-16), ~v=`zero)]),
+      Media.mobile([margin2(~h=`px(-15), ~v=`zero)]),
     ]);
   let header =
     style([
@@ -37,7 +37,7 @@ module Styles = {
 };
 
 let button = (~name, ~route, ~active) => {
-  <Link key=name className={Styles.buttonContainer(active)} route>
+  <Link key=name isTab=true className={Styles.buttonContainer(active)} route>
     <Text
       value=name
       weight=Text.Regular
```
