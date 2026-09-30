# [?] fix(relayer): fix a panic in relayer-api (#16720)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2024-04-12
Source: https://github.com/taikoxyz/taiko-mono/commit/e992ec902583c9f726bf915c6fd7b00289977460
Type: security-commit

## Details
fix(relayer): fix a panic in relayer-api (#16720)

## Patch
### packages/relayer/api/api.go
```diff
@@ -85,6 +85,7 @@ func InitFromConfig(ctx context.Context, api *API, cfg *Config) (err error) {
 	api.httpPort = cfg.HTTPPort
 	api.ctx = ctx
 	api.wg = &sync.WaitGroup{}
+	api.srcEthClient = srcEthClient
 
 	return nil
 }
```
