# [?] Fix JSONGetMethod to prevent panics on bad input.

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2014-09-16
Source: https://github.com/btcsuite/btcd/commit/26802c7eccfb484141a1488c9ef40e5b5805d96c
Type: security-commit

## Details
Fix JSONGetMethod to prevent panics on bad input.

ok @jcvernaleo

## Patch
### jsonapi.go
```diff
@@ -618,26 +618,11 @@ func CreateMessageWithId(message string, id interface{}, args ...interface{}) ([
 // JSONGetMethod takes a message and tries to find the bitcoin command that it
 // is in reply to so it can be processed further.
 func JSONGetMethod(message []byte) (string, error) {
-	// Need this so we can tell what kind of message we are sending
-	// so we can unmarshal it properly.
-	var method string
-	var msg interface{}
-	err := json.Unmarshal(message, &msg)
-	if err != nil {
-		err := fmt.Errorf("error, message does not appear to be valid json: %v", err)
-		return method, err
-	}
-	m := msg.(map[string]interface{})
-	for k, v := range m {
-		if k == "method" {
-			method = v.(string)
-		}
-	}
-	if method == "" {
-		err := fmt.Errorf("error, no method specified")
-		return method, err
+	var obj struct {
+		Method string `json:"method"`
 	}
-	return method, err
+	err := json.Unmarshal(message, &obj)
+	return obj.Method, err
 }
 
 // TlsRpcCommand takes a message generated from one of the routines above
```
