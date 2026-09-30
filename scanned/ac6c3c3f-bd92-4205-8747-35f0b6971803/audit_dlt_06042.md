# [?] fixed: ioctl  node delegate crashes if ROLLDPOS not register (#2390) (#2398)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2020-08-20
Source: https://github.com/iotexproject/iotex-core/commit/97902627dc8d1e7af4b483de502acee829c12b26
Type: security-commit

## Details
fixed: ioctl  node delegate crashes if ROLLDPOS not register (#2390) (#2398)

* fixed: ioctl  node delegate crashes if ROLLDPOS not register (#2390)

In standalone mode or no consensus configurations mode, `ioctl node delegate` or `ioctl node probationlist` will crash cause no consensus registered.

* assign value to epochNum

Co-authored-by: dustinxie <dahuaxie@gmail.com>

## Patch
### ioctl/cmd/node/nodedelegate.go
```diff
@@ -70,7 +70,6 @@ var nodeDelegateCmd = &cobra.Command{
 		cmd.SilenceUsage = true
 		err := delegates()
 		return output.PrintError(err)
-
 	},
 }
 
@@ -128,7 +127,11 @@ func delegates() error {
 		if err != nil {
 			return output.NewError(0, "failed to get chain meta", err)
 		}
-		epochNum = chainMeta.Epoch.Num
+		epochData := chainMeta.GetEpoch()
+		if epochData == nil {
+			return output.NewError(0, "ROLLDPOS is not registered", nil)
+		}
+		epochNum = epochData.Num
 	}
 	response, err := bc.GetEpochMeta(epochNum)
 	if err != nil {
```

### ioctl/cmd/node/nodeprobationlist.go
```diff
@@ -69,7 +69,11 @@ func probationlist() error {
 		if err != nil {
 			return output.NewError(0, "failed to get chain meta", err)
 		}
-		epochNum = chainMeta.Epoch.Num
+		epochData := chainMeta.GetEpoch()
+		if epochData == nil {
+			return output.NewError(0, "ROLLDPOS is not registered", nil)
+		}
+		epochNum = epochData.Num
 	}
 	response, err := bc.GetEpochMeta(epochNum)
 	if err != nil {
```
