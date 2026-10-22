# [H] in `farmPlots`

## Summary
Severity: High
Contest weight: 0.4973
Dataset id: 21751
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a logical accounting flaw in the internal _farmPlots routine that can cause every transaction that attempts to farm or unstake a plot to revert with a panic. The root cause is the way the number of plots owned by a landlord is calculated: it is derived by dividing the landlord’s locked weighted value by a mutable constant PRICE_PER_PLOT. When the protocol owner raises PRICE_PER_PLOT through a config update, the division yields a smaller plot count even though the landlord has not unlocked any funds. The code then checks whether the stored plot identifier of the user (_toiler.plotId) exceeds the current plot count. If it does, the routine falls back to using plotMetadata[landlord].lastUpdated as a timestamp for reward calculation. Because lastUpdated is only refreshed when the landlord locks or unlocks funds, it remains stale (often zero) when the plot count drops solely due to a price increase. The stale timestamp is then subtracted from _toiler.lastToilDate, which was set to the block timestamp at the moment the user staked. In Solidity 0.8+ this subtraction underflows and triggers an automatic revert, causing the whole _farmPlots call to panic. From a user’s perspective the UI shows that farming or withdrawing rewards fails silently, balances appear unchanged and the user receives no reward or refund despite having staked assets. The condition only manifests after a price change and only for landlords who have not interacted with the contract since the change, making it easy to miss during normal testing. The impact is a denial‑of‑service for affected users and a potential loss of funds because they cannot retrieve their staked tokens until the bug is fixed. The issue was discovered during a manual audit by tracing the reward‑calculation logic and noticing the unsafe timestamp subtraction. To remediate, the contract should either update landlord.lastUpdated whenever PRICE_PER_PLOT changes, or avoid using a stale timestamp by resetting the reference time to block.timestamp or by explicitly marking the toiler state as dirty and skipping the reward calculation until the landlord’s metadata is refreshed. In broader terms this is a classic case of a stale‑state dependent arithmetic error that violates the protocol’s accounting invariants, leading to negative time deltas and unintended reverts.

## Proof of Concept
The problem arises whenever `PRICE_PER_PLOT` gets increased through `configUpdated`. Whenever it gets increased, then `_getNumPlots` will return less numbers for that `LandLord`, because its denominated by `PRICE_PER_PLOT`.

File: LandManager.sol  
344:     function _getNumPlots(address _account) internal view returns (uint256) {  
345:         return lockManager.getLockedWeightedValue(_account) / PRICE_PER_PLOT;  
346:     }

For example:  
  * A user is staked in `plotId` 100, and the `LandLord` has 200 Plots.  
  * `PRICE_PER_PLOT` gets increased and makes the Plots of that `Landlord` to be 90.  
  * Now the user is staked to a `Plot` that is considered invalid and should be flagged as `dirty` of his `toilerState[tokenId]` struct.

Now, the problem here is that `NumPlots` is not decreased due to `LandLord` unlocking funds but instead due to `PRICE_PER_PLOT` getting increased -> meaning that `plotMetadata[landlord].lastUpdated` is too old.

In `_farmPlots` we see:  
File: LandManager.sol  
232:     function _farmPlots(address _sender) internal {  
//////////.............OmmitCode  
258:             if (_getNumPlots(landlord) < _toiler.plotId) {  
259:                 timestamp = plotMetadata[landlord].lastUpdated;  
260:                 toilerState[tokenId].dirty = true;  
261:             }  
//////////.............OmmitCode  
280:             schnibblesTotal =  
281:                 (timestamp - _toiler.lastToilDate) *  
282:                 BASE_SCHNIBBLE_RATE;  
//////////.............OmmitCode  
309:         accountManager.updatePlayer(mainAccount, renterMetadata);  
310:     }

In Line 258, we check for `NumPlots` if it’s lower than `plotId` of the user we then assign `timeStamp` variable to `landlord.lastUpdated` which is too old `timeStamp` (the last time the user locked funds).

Then in Line 281, we subtract `timestamp` (which is now `landlord.lastUpdated` which is too old `timeStamp`) from `_toiler.lastToilDate` which is larger than `timestamp` that will lead to panic revert.

Let’s see why `lastToilDate` is larger:  
We set this variable in `stakeMunchable` to `block.timestamp` here:  
File: LandManager.sol  
162:         toilerState[tokenId] = ToilerState({  
163:             lastToilDate: block.timestamp,  
164:             plotId: plotId,  
165:             landlord: landlord,  
166:             latestTaxRate: plotMetadata[landlord].currentTaxRate,  
167:             dirty: false  
168:         });

The `landlord.lastUpdated` is only updated when he lock or unlock funds (which in our case, didn’t lock or unlock any funds before the user stake to him).

## Recommendation
To avoid this case from happening, when `PRICE_PER_PLOT` gets increased we should check if `landlord.lastUpdated` is `>` than `_toiler.lastToilDate` inside the block (of this case `if (_getNumPlots(landlord) < _toiler.plotId)`), so that we can differentiate from cases that `LandLord` unlocked funds from cases where `PRICE_PER_PLOT` got increased and the `LandLord` didn’t do anything with his funds for a while.
