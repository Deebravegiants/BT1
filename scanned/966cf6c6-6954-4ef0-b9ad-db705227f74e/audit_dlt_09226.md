# [?] fix race condition when logging requests

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2021-02-27
Source: https://github.com/ipfs/kubo/commit/d631204deeea7da9ee9f6212fd23ef7b67dcebe2
Type: security-commit

## Details
fix race condition when logging requests

## Patch
### commands/context.go
```diff
@@ -117,7 +117,6 @@ func (c *Context) LogRequest(req *cmds.Request) func() {
 		Command:   strings.Join(req.Path, "/"),
 		Options:   req.Options,
 		Args:      req.Arguments,
-		ID:        c.ReqLog.nextID,
 		log:       c.ReqLog,
 	}
 	c.ReqLog.AddEntry(rle)
```

### commands/reqlog.go
```diff
@@ -38,6 +38,7 @@ func (rl *ReqLog) AddEntry(rle *ReqLogEntry) {
 	rl.lock.Lock()
 	defer rl.lock.Unlock()
 
+	rle.ID = rl.nextID
 	rl.nextID++
 	rl.Requests = append(rl.Requests, rle)
 
```
