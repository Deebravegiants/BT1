# [?] p2p/protocols: fix race condition in TestAccountingSimulation (#19228)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-03-07
Source: https://github.com/celo-org/celo-blockchain/commit/f2d63103541ee3746ff0834e7c69d188af3572d2
Type: security-commit

## Details
p2p/protocols: fix race condition in TestAccountingSimulation (#19228)

p2p/protocols: Fix race condition in TestAccountingSimulation

## Patch
### p2p/protocols/accounting_simulation_test.go
```diff
@@ -159,8 +159,9 @@ func TestAccountingSimulation(t *testing.T) {
 // (n entries in the array will not be filled -
 //  the balance of a node with itself)
 type matrix struct {
-	n int     //number of nodes
-	m []int64 //array of balances
+	n    int     //number of nodes
+	m    []int64 //array of balances
+	lock sync.RWMutex
 }
 
 // create a new matrix
@@ -177,7 +178,9 @@ func (m *matrix) add(i, j int, v int64) error {
 	// i * number of nodes + remote node
 	mi := i*m.n + j
 	// register that balance
+	m.lock.Lock()
 	m.m[mi] += v
+	m.lock.Unlock()
 	return nil
 }
 
```
