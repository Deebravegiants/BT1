# [?] Fix worng message on restore crash db. (#3455)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2022-01-20
Source: https://github.com/algorand/go-algorand/commit/33b87c432065d3be0ce1fdad682604f416676133
Type: security-commit

## Details
Fix worng message on restore crash db. (#3455)

When crash state is found but could not be restored, noCrashState variable is used to report a warning.
However, this variable was set to false in a case where there was no crash state, and the wrong warning was reported.

## Patch
### agreement/persistence.go
```diff
@@ -125,6 +125,7 @@ func restore(log logging.Logger, crash db.Accessor) (raw []byte, err error) {
 		// the above call was completed sucecssfully, which means that we've just created the table ( which wasn't there ! ).
 		// in that case, the table is guaranteed to be empty, and therefore we can return right here.
 		log.Infof("restore (agreement): crash state table initialized")
+		noCrashState = true // this is a normal case (we don't have crash state)
 		err = errNoCrashStateAvailable
 		return
 	}
```
