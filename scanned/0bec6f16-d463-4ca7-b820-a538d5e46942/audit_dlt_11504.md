# [?] fix overflow error on data source execution

## Summary
Severity: Unknown
Chain: Oracle
Component: bandprotocol/bandchain
Published: 2020-09-01
Source: https://github.com/bandprotocol/bandchain/commit/6e5a70a5b5cf92a226383131b523a6cde510f2a0
Type: security-commit

## Details
fix overflow error on data source execution

## Patch
### scan/src/components/data-source/DataSourceExecute.re
```diff
@@ -124,7 +124,7 @@ let resultRender = result => {
   | Error(err) =>
     <>
       <VSpacing size=Spacing.lg />
-      <div className=Styles.resultWrapper> <Text value=err /> </div>
+      <div className=Styles.resultWrapper> <Text value=err breakAll=true /> </div>
     </>
   | Success({returncode, stdout, stderr}) =>
     <div className=Styles.resultContainer>
```
