# [?] swarm/network: fix data race in stream.(*Peer).handleOfferedHashesMsg() (#18468)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-01-17
Source: https://github.com/celo-org/celo-blockchain/commit/4f8ec445653aa5131eb18fd6f821ed5fc284fd42
Type: security-commit

## Details
swarm/network: fix data race in stream.(*Peer).handleOfferedHashesMsg() (#18468)

* swarm/network: fix data race in stream.(*Peer).handleOfferedHashesMsg()

handleOfferedHashesMsg() contained a data race:
- read => in a goroutine, call to c.batchDone()
- write => in the main thread, write to c.sessionAt

c.batchDone() contained a call to c.AddInterval(). Client was a value
receiver for AddInterval. So on c.AddInterval() call the whole client
struct got copied (read) while one of its field was modified in
handleOfferedHashesMsg() (write).

fixes ethersphere/go-ethereum#1086

* swarm/network: simplify some trivial statements

## Patch
### swarm/network/stream/stream.go
```diff
@@ -666,17 +666,16 @@ func peerStreamIntervalsKey(p *Peer, s Stream) string {
 	return p.ID().String() + s.String()
 }
 
-func (c client) AddInterval(start, end uint64) (err error) {
+func (c *client) AddInterval(start, end uint64) (err error) {
 	i := &intervals.Intervals{}
-	err = c.intervalsStore.Get(c.intervalsKey, i)
-	if err != nil {
+	if err = c.intervalsStore.Get(c.intervalsKey, i); err != nil {
 		return err
 	}
 	i.Add(start, end)
 	return c.intervalsStore.Put(c.intervalsKey, i)
 }
 
-func (c client) NextInterval() (start, end uint64, err error) {
+func (c *client) NextInterval() (start, end uint64, err error) {
 	i := &intervals.Intervals{}
 	err = c.intervalsStore.Get(c.intervalsKey, i)
 	if err != nil {
@@ -733,11 +732,7 @@ func (c *client) batchDone(p *Peer, req *OfferedHashesMsg, hashes []byte) error
 		}
 		return nil
 	}
-	// TODO: make a test case for testing if the interval is added when the batch is done
-	if err := c.AddInterval(req.From, req.To); err != nil {
-		return err
-	}
-	return nil
+	return c.AddInterval(req.From, req.To)
 }
 
 func (c *client) close() {
```
