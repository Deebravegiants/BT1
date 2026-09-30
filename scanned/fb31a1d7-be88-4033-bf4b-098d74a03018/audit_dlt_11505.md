# [?] Merge pull request #2516 from bandprotocol/fix-thead-overflow-mobile

## Summary
Severity: Unknown
Chain: Oracle
Component: bandprotocol/bandchain
Published: 2020-08-21
Source: https://github.com/bandprotocol/bandchain/commit/a082f98ca7154c0b21d5d5344902763896962e26
Type: security-commit

## Details
Merge pull request #2516 from bandprotocol/fix-thead-overflow-mobile

Scan: fix loading and bg search

## Patch
### CHANGELOG_UNRELEASED.md
```diff
@@ -18,6 +18,8 @@
 
 ### Scan
 
+- (impv) [\#2516](https://github.com/bandprotocol/bandchain/pull/2516) Fix loading width and bg color
+
 ### Bridges
 
 ### Runtime
```

### scan/src/components/ChainIDBadge.re
```diff
@@ -149,19 +149,10 @@ let make = () =>
   }
   |> Sub.default(
        _,
-       <div className=Styles.versionLoading>
-         {Media.isMobile()
-            ? <LoadingCensorBar
-                width=110
-                height=20
-                colorBase=Colors.blue1
-                colorLighter=Colors.white
-              />
-            : <LoadingCensorBar
-                width=120
-                height=16
-                colorBase=Colors.blue1
-                colorLighter=Colors.white
-              />}
-       </div>,
+       {
+         let width = Media.isSmallMobile() ? 80 : 110;
+         <div className=Styles.versionLoading>
+           <LoadingCensorBar width height=20 colorBase=Colors.blue1 colorLighter=Colors.white />
+         </div>;
+       },
      );
```

### scan/src/components/UserAccount.re
```diff
@@ -178,12 +178,11 @@ let make = () => {
     <div className={CssHelper.flexBox(~justify=`flexEnd, ())}>
       {switch (trackingSub) {
        | Data({chainID}) => <ConnectBtn connect={_ => connect(chainID)} />
-
        | Error(err) =>
          // log for err details
          Js.Console.log(err);
          <Text value="chain id not found" />;
-       | _ => <LoadingCensorBar width=60 height=18 />
+       | _ => <LoadingCensorBar width=80 height=18 />
        }}
     </div>
   };
```
