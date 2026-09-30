# [?] caplin: Fix `nil` panic during error handling (#13333)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-01-06
Source: https://github.com/erigontech/erigon/commit/dc547a8f1d556b330f87eabf6ab338c0027cf206
Type: security-commit

## Details
caplin: Fix `nil` panic during error handling (#13333)

Fixes #13332

## Patch
### cl/beacon/beaconhttp/api.go
```diff
@@ -106,6 +106,8 @@ func HandleEndpoint[T any](h EndpointHandler[T]) http.HandlerFunc {
 			var e *EndpointError
 			if errors.As(err, &e) {
 				endpointError = e
+			} else {
+				endpointError = WrapEndpointError(err)
 			}
 			endpointError.WriteTo(w)
 			return
```
