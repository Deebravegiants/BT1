# [?] fix: disperser client deadlock (#1688)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2025-06-26
Source: https://github.com/Layr-Labs/eigenda/commit/c309737f2d62ea84eb87eca6981211c39e2e59b6
Type: security-commit

## Details
fix: disperser client deadlock (#1688)

disperser client was not unlocking the accountantLock in one error path, which was causing proxy to deadlock when retrying.

## Patch
### api/clients/v2/disperser_client.go
```diff
@@ -208,6 +208,7 @@ func (c *disperserClient) DisperseBlobWithProbe(
 
 	err = c.initOncePopulateAccountant(ctx)
 	if err != nil {
+		c.accountantLock.Unlock()
 		return nil, [32]byte{}, api.NewErrorFailover(err)
 	}
 
```
