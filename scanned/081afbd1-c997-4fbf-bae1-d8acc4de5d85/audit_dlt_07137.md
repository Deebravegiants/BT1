# [?] rpc: fix rare deadlock when canceling HTTP call context (#19715)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-06-20
Source: https://github.com/celo-org/celo-blockchain/commit/8d815e365cd2cda2e865dd2e272ebb5a3d4b8772
Type: security-commit

## Details
rpc: fix rare deadlock when canceling HTTP call context (#19715)

When cancelling the context for a call on a HTTP-based client while the
call is running, the select in requestOp.wait may hit the <-context.Done()
case instead of the <-op.resp case. This doesn't happen often -- our
cancel test hasn't caught this even though it ran thousands of times
on CI since the RPC client was added.

Fixes #19714

## Patch
### rpc/client.go
```diff
@@ -137,9 +137,11 @@ func (op *requestOp) wait(ctx context.Context, c *Client) (*jsonrpcMessage, erro
 	select {
 	case <-ctx.Done():
 		// Send the timeout to dispatch so it can remove the request IDs.
-		select {
-		case c.reqTimeout <- op:
-		case <-c.closing:
+		if !c.isHTTP {
+			select {
+			case c.reqTimeout <- op:
+			case <-c.closing:
+			}
 		}
 		return nil, ctx.Err()
 	case resp := <-op.resp:
```
