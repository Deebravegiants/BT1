# [?] [node.sh] fix a race condition in bls loader test

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-07-13
Source: https://github.com/harmony-one/harmony/commit/dd62845f094117dd70f5918ceeeb27005b610853
Type: security-commit

## Details
[node.sh] fix a race condition in bls loader test

## Patch
### cmd/harmony/blsloader/kms.go
```diff
@@ -226,8 +226,9 @@ func (provider *promptACProvider) prompt(hint string) (string, error) {
 		timedOut = time.After(provider.timeout)
 	)
 
+	cs := console
 	go func() {
-		res, err = provider.threadedPrompt(hint)
+		res, err = provider.threadedPrompt(cs, hint)
 		close(finished)
 	}()
 
@@ -241,9 +242,9 @@ func (provider *promptACProvider) prompt(hint string) (string, error) {
 	}
 }
 
-func (provider *promptACProvider) threadedPrompt(hint string) (string, error) {
-	console.print(hint)
-	return console.readPassword()
+func (provider *promptACProvider) threadedPrompt(cs consoleItf, hint string) (string, error) {
+	cs.print(hint)
+	return cs.readPassword()
 }
 
 func kmsClientWithConfig(config *AwsConfig) (*kms.KMS, error) {
```
