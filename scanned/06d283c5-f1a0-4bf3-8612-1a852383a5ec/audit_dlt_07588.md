# [?] graphql: fix nil deref on a timer (#27978)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-08-23
Source: https://github.com/ethereum/go-ethereum/commit/c31f9cf23a7335b04ee98cd3671d12bf5834e02a
Type: security-commit

## Details
graphql: fix nil deref on a timer (#27978)

graphql: fix the panic of nil timer.Stop

Signed-off-by: jsvisa <delweng@gmail.com>

## Patch
### graphql/service.go
```diff
@@ -88,7 +88,9 @@ func (h handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
 	}
 
 	response := h.Schema.Exec(ctx, params.Query, params.OperationName, params.Variables)
-	timer.Stop()
+	if timer != nil {
+		timer.Stop()
+	}
 	responded.Do(func() {
 		responseJSON, err := json.Marshal(response)
 		if err != nil {
```
