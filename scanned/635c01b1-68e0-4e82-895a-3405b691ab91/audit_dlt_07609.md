# [?] consensus/clique: fix race condition (#24957)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2022-05-30
Source: https://github.com/ethereum/go-ethereum/commit/88452273061060c0f5704aa66f7a030bb82d8e12
Type: security-commit

## Details
consensus/clique: fix race condition (#24957)

* consensus/clique: remove race condition

* consensus/clique: fix one more signer data race

Co-authored-by: Gary Rong <garyrong0905@gmail.com>

## Patch
### consensus/clique/clique.go
```diff
@@ -180,7 +180,7 @@ type Clique struct {
 
 	signer common.Address // Ethereum address of the signing key
 	signFn SignerFn       // Signer function to authorize hashes with
-	lock   sync.RWMutex   // Protects the signer fields
+	lock   sync.RWMutex   // Protects the signer and proposals fields
 
 	// The fields below are for testing only
 	fakeDiff bool // Skip difficulty verifications
@@ -507,9 +507,8 @@ func (c *Clique) Prepare(chain consensus.ChainHeaderReader, header *types.Header
 	if err != nil {
 		return err
 	}
+	c.lock.RLock()
 	if number%c.config.Epoch != 0 {
-		c.lock.RLock()
-
 		// Gather all the proposals that make sense voting on
 		addresses := make([]common.Address, 0, len(c.proposals))
 		for address, authorize := range c.proposals {
@@ -526,10 +525,14 @@ func (c *Clique) Prepare(chain consensus.ChainHeaderReader, header *types.Header
 				copy(header.Nonce[:], nonceDropVote)
 			}
 		}
-		c.lock.RUnlock()
 	}
+
+	// Copy signer protected by mutex to avoid race condition
+	signer := c.signer
+	c.lock.RUnlock()
+
 	// Set the correct difficulty
-	header.Difficulty = calcDifficulty(snap, c.signer)
+	header.Difficulty = calcDifficulty(snap, signer)
 
 	// Ensure the extra data has all its components
 	if len(header.Extra) < extraVanity {
@@ -666,7 +669,10 @@ func (c *Clique) CalcDifficulty(chain consensus.ChainHeaderReader, time uint64,
 	if err != nil {
 		return nil
 	}
-	return calcDifficulty(snap, c.signer)
+	c.lock.RLock()
+	signer := c.signer
+	c.lock.RUnlock()
+	return calcDifficulty(snap, signer)
 }
 
 func calcDifficulty(snap *Snapshot, signer common.Address) *big.Int {
```
