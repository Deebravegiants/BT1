# [?] Merge pull request #4081 from oasisprotocol/ptrus/fix/ias-proxy-panic

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2021-06-25
Source: https://github.com/oasisprotocol/oasis-core/commit/99abb0ff21b7a75cda61a78e3573d837abf695ff
Type: security-commit

## Details
Merge pull request #4081 from oasisprotocol/ptrus/fix/ias-proxy-panic

ias/proxy: return error in GetSigRL if mock client is used

## Patch
### .changelog/4081.bugfix.md
```diff
@@ -0,0 +1 @@
+ias/proxy/client: `GetSigRL` don't panic if IAS proxy not configured
```

### go/ias/proxy/client/client.go
```diff
@@ -80,6 +80,9 @@ func (c *proxyClient) GetSPIDInfo(ctx context.Context) (*api.SPIDInfo, error) {
 }
 
 func (c *proxyClient) GetSigRL(ctx context.Context, epidGID uint32) ([]byte, error) {
+	if c.endpoint == nil {
+		return nil, fmt.Errorf("IAS proxy is not configured, mock used")
+	}
 	return c.endpoint.GetSigRL(ctx, epidGID)
 }
 
```
