# [?] consensus/clique: fix race condition (#24957) (#766)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2024-05-23
Source: https://github.com/scroll-tech/go-ethereum/commit/fe55edda0f1d155875e3ed75ad8551c11f6fba67
Type: security-commit

## Details
consensus/clique: fix race condition (#24957) (#766)

## Patch
### consensus/clique/clique.go
```diff
@@ -181,7 +181,7 @@ type Clique struct {
 
 	signer common.Address // Ethereum address of the signing key
 	signFn SignerFn       // Signer function to authorize hashes with
-	lock   sync.RWMutex   // Protects the signer fields
+	lock   sync.RWMutex   // Protects the signer and proposals fields
 
 	// The fields below are for testing only
 	fakeDiff bool // Skip difficulty verifications
@@ -509,9 +509,8 @@ func (c *Clique) Prepare(chain consensus.ChainHeaderReader, header *types.Header
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
@@ -528,10 +527,14 @@ func (c *Clique) Prepare(chain consensus.ChainHeaderReader, header *types.Header
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
@@ -670,7 +673,10 @@ func (c *Clique) CalcDifficulty(chain consensus.ChainHeaderReader, time uint64,
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

### params/version.go
```diff
@@ -24,7 +24,7 @@ import (
 const (
 	VersionMajor = 5         // Major version component of the current release
 	VersionMinor = 3         // Minor version component of the current release
-	VersionPatch = 19        // Patch version component of the current release
+	VersionPatch = 20        // Patch version component of the current release
 	VersionMeta  = "mainnet" // Version metadata to append to the version string
 )
 
```
