# [?] grpcLachesisProxy data race fix

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-06-24
Source: https://github.com/0xsoniclabs/sonic/commit/53ce1cbf632a62d870fe3638ab9e8c9a2d7b52e6
Type: security-commit

## Details
grpcLachesisProxy data race fix

## Patch
### src/proxy/grpc_lachesis.go
```diff
@@ -85,16 +85,14 @@ func (p *grpcLachesisProxy) Close() {
 
 	p.closeStream()
 	err := p.conn.Close()
-
-	close(p.commitCh)
-	close(p.queryCh)
-	close(p.restoreCh)
-
 	if err != nil {
 		p.Error(err)
 	}
 
 	p.wg.Wait()
+	close(p.commitCh)
+	close(p.queryCh)
+	close(p.restoreCh)
 }
 
 /*
```
