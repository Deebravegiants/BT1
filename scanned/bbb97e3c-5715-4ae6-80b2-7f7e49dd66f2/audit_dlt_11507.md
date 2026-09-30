# [?] :bug: Fixed overflow issue and update default tab

## Summary
Severity: Unknown
Chain: Oracle
Component: bandprotocol/bandchain
Published: 2020-08-18
Source: https://github.com/bandprotocol/bandchain/commit/0779c5dc6c2ee45f3dc31924f75c6a0f14700413
Type: security-commit

## Details
:bug: Fixed overflow issue and update default tab

## Patch
### scan/src/pages/OracleScriptIndexPage.re
```diff
@@ -48,7 +48,6 @@ let make = (~oracleScriptID, ~hashtag: Route.oracle_script_tab_t) => {
                      <Text
                        value={request |> Format.iPretty}
                        size=Text.Xxl
-                       weight=Text.Regular
                        align=Text.Center
                        block=true
                      />
@@ -67,7 +66,7 @@ let make = (~oracleScriptID, ~hashtag: Route.oracle_script_tab_t) => {
                     <HSpacing size=Spacing.xs />
                     //TODO: remove mock message later
                     <CTooltip
-                      tooltipPlacementSm=CTooltip.BottomLeft
+                      tooltipPlacementSm=CTooltip.BottomRight
                       tooltipText="Lorem ipsum, or lipsum as it is sometimes known.">
                       <Icon name="fal fa-info-circle" size=12 />
                     </CTooltip>
@@ -77,7 +76,6 @@ let make = (~oracleScriptID, ~hashtag: Route.oracle_script_tab_t) => {
                      <Text
                        value={responseTime |> Format.iPretty}
                        size=Text.Xxl
-                       weight=Text.Regular
                        align=Text.Center
                        block=true
                      />
@@ -146,15 +144,7 @@ let make = (~oracleScriptID, ~hashtag: Route.oracle_script_tab_t) => {
             <Heading value="Description" size=Heading.H5 marginBottom=16 />
             {switch (oracleScriptSub) {
              | Data({description}) =>
-               <p>
-                 <Text
-                   value=description
-                   weight=Text.Regular
-                   size=Text.Lg
-                   color=Colors.gray7
-                   block=true
-                 />
-               </p>
+               <p> <Text value=description size=Text.Lg color=Colors.gray7 block=true /> </p>
              | _ => <LoadingCensorBar width=284 height=15 />
              }}
           </div>
```

### scan/src/utils/ID.re
```diff
@@ -19,7 +19,7 @@ module RawOracleScriptID = {
   let prefix = "#O";
   let color = Colors.pink5;
   let route = (id, tab) => Route.OracleScriptIndexPage(id, tab);
-  let defaultTab = Route.OracleScriptExecute;
+  let defaultTab = Route.OracleScriptRequests;
 };
 
 module RawRequestID = {
```
