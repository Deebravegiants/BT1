# [?] fix: correct panic messages and enforce sealing check in SetStreamingManager (#23951)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-03-20
Source: https://github.com/cosmos/cosmos-sdk/commit/a9e7d5b5ad3ed51484742f8402227ce45861f725
Type: security-commit

## Details
fix: correct panic messages and enforce sealing check in SetStreamingManager (#23951)

## Patch
### CHANGELOG.md
```diff
@@ -86,6 +86,7 @@ Every module contains its own CHANGELOG.md. Please refer to the module you are i
 
 ### Improvements
 
+* (baseapp) [#23951](https://github.com/cosmos/cosmos-sdk/pull/23951) Corrected panic messages in `SetCMS` and `SetCheckTxHandler`, and enforced `sealed` check in `SetStreamingManager` for consistency with other setters.
 * [#23470](https://github.com/cosmos/cosmos-sdk/pull/23470) Converge to use of one single sign mode type and signer data:
   * Use api's signmode throughout the SDK to align with `cosmossdk.io/tx`. This allows developer not to juggle between sign mode types
   * Deprecate `authsigning.SignerData` in favor of txsigning.SignerData and replace its usage
```

### baseapp/options.go
```diff
@@ -182,7 +182,7 @@ func (app *BaseApp) SetDB(db corestore.KVStoreWithBatch) {
 
 func (app *BaseApp) SetCMS(cms storetypes.CommitMultiStore) {
 	if app.sealed {
-		panic("SetEndBlocker() on sealed BaseApp")
+		panic("SetCMS() on sealed BaseApp")
 	}
 
 	app.cms = cms
@@ -375,7 +375,7 @@ func (app *BaseApp) SetPrepareProposal(handler sdk.PrepareProposalHandler) {
 // SetCheckTxHandler sets the checkTx function for the BaseApp.
 func (app *BaseApp) SetCheckTxHandler(handler sdk.CheckTxHandler) {
 	if app.sealed {
-		panic("SetCheckTx() on sealed BaseApp")
+		panic("SetCheckTxHandler() on sealed BaseApp")
 	}
 
 	app.checkTxHandler = handler
@@ -408,6 +408,9 @@ func (app *BaseApp) SetStoreMetrics(gatherer metrics.StoreMetrics) {
 
 // SetStreamingManager sets the streaming manager for the BaseApp.
 func (app *BaseApp) SetStreamingManager(manager storetypes.StreamingManager) {
+	if app.sealed {
+		panic("SetStreamingManager() on sealed BaseApp")
+	}
 	app.streamingManager = manager
 }
 
```
