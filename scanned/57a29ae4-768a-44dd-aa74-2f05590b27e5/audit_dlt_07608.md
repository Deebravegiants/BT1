# [?] p2p/discover: fix panicky test (#25038)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2022-06-07
Source: https://github.com/ethereum/go-ethereum/commit/403624a4a17bf99b74e50343024a07fe54c53fa7
Type: security-commit

## Details
p2p/discover: fix panicky test (#25038)

## Patch
### p2p/discover/v4_udp_test.go
```diff
@@ -284,6 +284,7 @@ func TestUDPv4_findnode(t *testing.T) {
 		test.waitPacketOut(func(p *v4wire.Neighbors, to *net.UDPAddr, hash []byte) {
 			if len(p.Nodes) != len(want) {
 				t.Errorf("wrong number of results: got %d, want %d", len(p.Nodes), bucketSize)
+				return
 			}
 			for i, n := range p.Nodes {
 				if n.ID.ID() != want[i].ID() {
```
