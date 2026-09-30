# [?] fix race condition when pinging peers (#13701)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2024-03-07
Source: https://github.com/OffchainLabs/prysm/commit/46085694954ede3a0c619c5d927581c2475b70d6
Type: security-commit

## Details
fix race condition when pinging peers (#13701)

## Patch
### beacon-chain/p2p/service.go
```diff
@@ -56,6 +56,7 @@ type Service struct {
 	started               bool
 	isPreGenesis          bool
 	pingMethod            func(ctx context.Context, id peer.ID) error
+	pingMethodLock        sync.RWMutex
 	cancel                context.CancelFunc
 	cfg                   *Config
 	peers                 *peers.Status
@@ -354,10 +355,14 @@ func (s *Service) MetadataSeq() uint64 {
 // AddPingMethod adds the metadata ping rpc method to the p2p service, so that it can
 // be used to refresh ENR.
 func (s *Service) AddPingMethod(reqFunc func(ctx context.Context, id peer.ID) error) {
+	s.pingMethodLock.Lock()
 	s.pingMethod = reqFunc
+	s.pingMethodLock.Unlock()
 }
 
 func (s *Service) pingPeers() {
+	s.pingMethodLock.RLock()
+	defer s.pingMethodLock.RUnlock()
 	if s.pingMethod == nil {
 		return
 	}
```
