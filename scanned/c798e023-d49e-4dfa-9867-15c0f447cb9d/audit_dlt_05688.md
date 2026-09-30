# [?] p2p/simulations: fix unlikely crash in probabilistic connect (#23200)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-07-29
Source: https://github.com/celo-org/celo-blockchain/commit/8f11d279d241cfdf2571d4fa772dc38efc6175d0
Type: security-commit

## Details
p2p/simulations: fix unlikely crash in probabilistic connect (#23200)

When the nodeCount is less than 10, it will panic with the out of bound error.
How about we just skip this round, when rand1 and rand2 are equal?

## Patch
### p2p/simulations/mocker.go
```diff
@@ -123,20 +123,12 @@ func probabilistic(net *Network, quit chan struct{}, nodeCount int) {
 		randWait := time.Duration(rand.Intn(5000)+1000) * time.Millisecond
 		rand1 := rand.Intn(nodeCount - 1)
 		rand2 := rand.Intn(nodeCount - 1)
-		if rand1 < rand2 {
+		if rand1 <= rand2 {
 			lowid = rand1
 			highid = rand2
 		} else if rand1 > rand2 {
 			highid = rand1
 			lowid = rand2
-		} else {
-			if rand1 == 0 {
-				rand2 = 9
-			} else if rand1 == 9 {
-				rand1 = 0
-			}
-			lowid = rand1
-			highid = rand2
 		}
 		var steps = highid - lowid
 		wg.Add(steps)
```
