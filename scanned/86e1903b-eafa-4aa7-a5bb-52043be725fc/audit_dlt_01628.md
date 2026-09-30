# [?] Fix race condition in `gossipVotesRoutine` (#692)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2023-04-11
Source: https://github.com/cometbft/cometbft/commit/85441ab257a01ba904fdf62b5da33e7e6e9c5b5a
Type: security-commit

## Details
Fix race condition in `gossipVotesRoutine` (#692)

* Repro in e2e tests

* Increase chances of data race

* Exacerbate race condition (2nd try)

* Fix race condition in `gossipVotesRoutine`

* Revert logic to expose data race

* RAII lock

## Patch
### consensus/reactor.go
```diff
@@ -744,7 +744,13 @@ OUTER_LOOP:
 			// Load the block's extended commit for prs.Height,
 			// which contains precommit signatures for prs.Height.
 			var ec *types.ExtendedCommit
-			if conR.conS.state.ConsensusParams.ABCI.VoteExtensionsEnabled(prs.Height) {
+			var veEnabled bool
+			func() {
+				conR.conS.mtx.RLock()
+				defer conR.conS.mtx.RUnlock()
+				veEnabled = conR.conS.state.ConsensusParams.ABCI.VoteExtensionsEnabled(prs.Height)
+			}()
+			if veEnabled {
 				ec = conR.conS.blockStore.LoadBlockExtendedCommit(prs.Height)
 			} else {
 				ec = conR.conS.blockStore.LoadBlockCommit(prs.Height).WrappedExtendedCommit()
```

### test/e2e/Makefile
```diff
@@ -14,7 +14,7 @@ docker:
 # order to build a binary with a CometBFT node in it (for built-in
 # ABCI testing).
 node:
-	go build $(BUILD_FLAGS) -tags '$(BUILD_TAGS)' -o build/node ./node
+	go build -race $(BUILD_FLAGS) -tags '$(BUILD_TAGS)' -o build/node ./node
 
 generator:
 	go build -o build/generator ./generator
```

### test/e2e/docker/Dockerfile
```diff
@@ -25,6 +25,7 @@ RUN cd test/e2e && make node && cp build/node /usr/bin/app
 WORKDIR /cometbft
 VOLUME /cometbft
 ENV CMTHOME=/cometbft
+ENV GORACE "halt_on_error=1"
 
 EXPOSE 26656 26657 26660 6060
 ENTRYPOINT ["/usr/bin/entrypoint"]
```
