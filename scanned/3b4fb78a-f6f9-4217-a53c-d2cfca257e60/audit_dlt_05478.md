# [?] fix(sync): check height bound to avoid overflow (#1537)

## Summary
Severity: Unknown
Chain: Rollkit
Component: rollkit/rollkit
Published: 2024-03-06
Source: https://github.com/evstack/ev-node/commit/f61fa09916be6d25bc87654bf09d4d0eab847a3c
Type: security-commit

## Details
fix(sync): check height bound to avoid overflow (#1537)

## Overview

This PR adds an additional check to block height during sync. This
avoids potential integer overflow. Fixes #1455

## Checklist

- [ ] New and updated code has appropriate documentation
- [ ] New and updated code has new and/or updated testing
- [ ] Required CI checks are passing
- [ ] Visual proof for any user facing features like CLI or
documentation updates
- [ ] Linked issues closed with keywords


<!-- This is an auto-generated comment: release notes by coderabbit.ai
-->

## Summary by CodeRabbit

- **Bug Fixes**
- Added a validation check to prevent negative initial height values in
block and header synchronization processes.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Patch
### block/block_sync.go
```diff
@@ -99,6 +99,9 @@ func (bSyncService *BlockSyncService) initBlockStoreAndStartSyncer(ctx context.C
 // Note: Only returns an error in case block store can't be initialized. Logs
 // error if there's one while broadcasting.
 func (bSyncService *BlockSyncService) WriteToBlockStoreAndBroadcast(ctx context.Context, block *types.Block) error {
+	if bSyncService.genesis.InitialHeight < 0 {
+		return fmt.Errorf("invalid initial height; cannot be negative")
+	}
 	isGenesis := block.Height() == uint64(bSyncService.genesis.InitialHeight)
 	// For genesis block initialize the store and start the syncer
 	if isGenesis {
```

### block/header_sync.go
```diff
@@ -98,6 +98,9 @@ func (hSyncService *HeaderSyncService) initHeaderStoreAndStartSyncer(ctx context
 // WriteToHeaderStoreAndBroadcast initializes header store if needed and broadcasts provided header.
 // Note: Only returns an error in case header store can't be initialized. Logs error if there's one while broadcasting.
 func (hSyncService *HeaderSyncService) WriteToHeaderStoreAndBroadcast(ctx context.Context, signedHeader *types.SignedHeader) error {
+	if hSyncService.genesis.InitialHeight < 0 {
+		return fmt.Errorf("invalid initial height; cannot be negative")
+	}
 	isGenesis := signedHeader.Height() == uint64(hSyncService.genesis.InitialHeight)
 	// For genesis header initialize the store and start the syncer
 	if isGenesis {
```
