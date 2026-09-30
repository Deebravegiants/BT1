# [?] p2p/protocols: fix rare data race in Peer.Handshake() (#18951)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-01-29
Source: https://github.com/celo-org/celo-blockchain/commit/a0ac3b6a1a1818285b74d9580c6d331837ec2e31
Type: security-commit

## Details
p2p/protocols: fix rare data race in Peer.Handshake() (#18951)

## Patch
### p2p/protocols/protocol.go
```diff
@@ -386,10 +386,12 @@ func (p *Peer) handleIncoming(handle func(ctx context.Context, msg interface{})
 // * the dialing peer needs to send the handshake first and then waits for remote
 // * the listening peer waits for the remote handshake and then sends it
 // returns the remote handshake and an error
-func (p *Peer) Handshake(ctx context.Context, hs interface{}, verify func(interface{}) error) (rhs interface{}, err error) {
+func (p *Peer) Handshake(ctx context.Context, hs interface{}, verify func(interface{}) error) (interface{}, error) {
 	if _, ok := p.spec.GetCode(hs); !ok {
 		return nil, errorf(ErrHandshake, "unknown handshake message type: %T", hs)
 	}
+
+	var rhs interface{}
 	errc := make(chan error, 2)
 	handle := func(ctx context.Context, msg interface{}) error {
 		rhs = msg
@@ -412,6 +414,7 @@ func (p *Peer) Handshake(ctx context.Context, hs interface{}, verify func(interf
 	}()
 
 	for i := 0; i < 2; i++ {
+		var err error
 		select {
 		case err = <-errc:
 		case <-ctx.Done():
```
