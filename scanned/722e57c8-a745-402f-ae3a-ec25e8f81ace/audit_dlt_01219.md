# [?] cl/sentinel: fix panic on short attnets ENR entry (#20492)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-04-11
Source: https://github.com/erigontech/erigon/commit/933f98664152b7dd1004e65cef6ce0e38e33b9b5
Type: security-commit

## Details
cl/sentinel: fix panic on short attnets ENR entry (#20492)

## Summary
Fixes a panic seen in the wild:

```
panic: runtime error: index out of range [4] with length 1
  cl/sentinel.(*Sentinel).findPeersForSubnets.func1
        cl/sentinel/discovery.go:80
```

A malformed/short `attnets` ENR entry decodes into a
`bitfield.Bitvector64` shorter than the expected 8 bytes, so indexing
`peerSubnets[subnetIdx/8]` goes out of range when `subnetIdx >= 8`.

Adds a `len(peerSubnets) == 8` guard at all three call sites in
`cl/sentinel/discovery.go` (`findPeersForSubnets` filter, post-connect
coverage update, and `onConnection` underserved-subnet check).

## Patch
### cl/sentinel/discovery.go
```diff
@@ -73,6 +73,9 @@ func (s *Sentinel) findPeersForSubnets(subnets []subnetSearchState) {
 		if err := node.Load(enr.WithEntry(s.cfg.NetworkConfig.AttSubnetKey, &peerSubnets)); err != nil {
 			return false
 		}
+		if len(peerSubnets) != 8 {
+			return false
+		}
 		// Check if this node covers any subnet we still need
 		for i := range subnets {
 			if subnets[i].found < subnets[i].wanted {
@@ -155,6 +158,9 @@ func (s *Sentinel) findPeersForSubnets(subnets []subnetSearchState) {
 		if err := node.Load(enr.WithEntry(s.cfg.NetworkConfig.AttSubnetKey, &peerSubnets)); err != nil {
 			continue
 		}
+		if len(peerSubnets) != 8 {
+			continue
+		}
 
 		coveredSubnets := []int{}
 		for i := range subnets {
@@ -549,7 +555,7 @@ func (s *Sentinel) onConnection(_ network.Network, conn network.Conn) {
 		if nodeVal, ok := s.pidToEnr.Load(peerId); ok {
 			if node, ok := nodeVal.(*enode.Node); ok {
 				var peerSubnets bitfield.Bitvector64
-				if err := node.Load(enr.WithEntry(s.cfg.NetworkConfig.AttSubnetKey, &peerSubnets)); err == nil {
+				if err := node.Load(enr.WithEntry(s.cfg.NetworkConfig.AttSubnetKey, &peerSubnets)); err == nil && len(peerSubnets) == 8 {
 					coverage := s.getSubnetCoverage()
 					for i := 0; i < attestationSubnetCount; i++ {
 						if peerSubnets[i/8]&(1<<(i%8)) != 0 && coverage[i] < minimumPeersPerSubnet {
```
