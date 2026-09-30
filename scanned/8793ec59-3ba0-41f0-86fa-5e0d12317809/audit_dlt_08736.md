# [?] fix: address race condition during EuclidV2 header chain verification (#1186)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2025-05-14
Source: https://github.com/scroll-tech/go-ethereum/commit/2500647c49ac7bcf54dd8c9f54f127ea10591361
Type: security-commit

## Details
fix: address race condition during EuclidV2 header chain verification (#1186)

## Patch
### consensus/wrapper/consensus.go
```diff
@@ -59,6 +59,31 @@ func (ue *UpgradableEngine) VerifyHeader(chain consensus.ChainHeaderReader, head
 	return ue.chooseEngine(header.Time).VerifyHeader(chain, header, seal)
 }
 
+func waitForHeader(chain consensus.ChainHeaderReader, header *types.Header) {
+	hash, number := header.Hash(), header.Number.Uint64()
+
+	// poll every 2 seconds, should succeed after a few tries
+	ticker := time.NewTicker(2 * time.Second)
+	defer ticker.Stop()
+
+	// we give up after 2 minutes
+	timeout := time.After(120 * time.Second)
+
+	for {
+		select {
+		case <-ticker.C:
+			// try reading from chain, if the header is present then we are ready
+			if h := chain.GetHeader(hash, number); h != nil {
+				return
+			}
+
+		case <-timeout:
+			log.Warn("Unable to find last pre-EuclidV2 header in chain", "hash", hash.Hex(), "number", number)
+			return
+		}
+	}
+}
+
 // VerifyHeaders verifies a batch of headers concurrently. In our use-case,
 // headers can only be all system, all clique, or start with clique and then switch once to system.
 func (ue *UpgradableEngine) VerifyHeaders(chain consensus.ChainHeaderReader, headers []*types.Header, seals []bool) (chan<- struct{}, <-chan error) {
@@ -124,10 +149,10 @@ func (ue *UpgradableEngine) VerifyHeaders(chain consensus.ChainHeaderReader, hea
 			}
 		}
 
-		// Not sure why we need this here, but without this we get err="unknown ancestor"
-		// at the 1st Euclid block. It seems that `VerifyHeaders` start processing the next
-		// header before the previous one was written into `chain`.
-		time.Sleep(2 * time.Second)
+		// `VerifyHeader` will try to call `chain.GetHeader`, which will race with `InsertHeaderChain`.
+		// This might result in "unknown ancestor" header validation error.
+		// This should be temporary, so we solve this by waiting here.
+		waitForHeader(chain, cliqueHeaders[len(cliqueHeaders)-1])
 
 		// Verify system contract headers.
 		log.Info("Start EuclidV2 transition verification in SystemContract section", "startBlockNumber", systemHeaders[0].Number, "endBlockNumber", systemHeaders[len(systemHeaders)-1].Number)
```

### params/version.go
```diff
@@ -24,7 +24,7 @@ import (
 const (
 	VersionMajor = 5         // Major version component of the current release
 	VersionMinor = 8         // Minor version component of the current release
-	VersionPatch = 45        // Patch version component of the current release
+	VersionPatch = 46        // Patch version component of the current release
 	VersionMeta  = "mainnet" // Version metadata to append to the version string
 )
 
```
