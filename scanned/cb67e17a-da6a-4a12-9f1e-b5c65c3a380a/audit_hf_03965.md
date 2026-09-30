# [M] PartyBFacetImpl.chargeFundingRate should

## Summary
Severity: Medium
Contest weight: 0.2601
Dataset id: 20321
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
File: symmio-core\contracts\facets\PartyB\PartyBFacetImpl.sol
310:
function chargeFundingRate(
311:
address partyA,
312:
uint256[] memory quoteIds,
313:
int256[] memory rates,
314:
PairUpnlSig memory upnlSig
315:
) internal {
316:
LibMuon.verifyPairUpnl(upnlSig, msg.sender, partyA);
317:
require(quoteIds.length == rates.length, "PartyBFacet: Length not match");
318:
int256 partyBAvailableBalance = LibAccount.partyBAvailableBalanceForLiquidation(
319:
upnlSig.upnlPartyB,
320:
msg.sender,
321:
partyA
322:
);
323:
int256 partyAAvailableBalance = LibAccount.partyAAvailableBalanceForLiquidation(
324:
upnlSig.upnlPartyA,
325:
partyA
326:
);
327:
uint256 epochDuration;
328:
uint256 windowTime;
329:
for (uint256 i = 0; i < quoteIds.length; i++) {
......//quoteIds is empty array, so code is never executed.
390:
}
391:
require(partyAAvailableBalance >= 0, "PartyBFacet: PartyA will be insolvent");
392:
require(partyBAvailableBalance >= 0, "PartyBFacet: PartyB will be insolvent");
393:
AccountStorage.layout().partyBNonces[msg.sender][partyA] += 1;
394:->
AccountStorage.layout().partyANonces[partyA] += 1;
395:
}
As long as partyBAvailableBalance(L318) and partyAAvailableBalance(L323) are greater than or equal to 0, that is to say, PartyA and PartyB are solvent. Then, partyB can add 1 to partyANonces[partyA] at little cost which is the gas of tx.
An example is given to illustrate how to cause losses for partyA. Assume that partyA requests to close a quote via [PartyAFacetImpl.requestToClosePosition](https://github.com/8-symmetrical/blob/main/symmio-core/contracts/facets/PartyA/PartyAFacetImpl.sol#L150). PartyB ignored it. partyA can only wait for maLayout.forceCloseCooldown seconds, and then call [PartyAFacetImpl.forceClosePosition](https://github.com/8-symmetrical/blob/main/symmio-core/contracts/facets/PartyA/PartyAFacetImpl.sol#L239) to forcefully close the quote.
File: symmio-core\contracts\facets\PartyA\PartyAFacetImpl.sol
239:
function forceClosePosition(uint256 quoteId, PairUpnlAndPriceSig memory upnlSig) internal {
240:
AccountStorage.Layout storage accountLayout = AccountStorage.layout();
241:
MAStorage.Layout storage maLayout = MAStorage.layout();
242:
Quote storage quote = QuoteStorage.layout().quotes[quoteId];
......//assume codes here are executed
273:->
LibMuon.verifyPairUpnlAndPrice(upnlSig, quote.partyB, quote.partyA, quote.symbolId);
Similarly, if partyA wants to deallocate funds via [AccountFacetImpl.deallocate](https://github.com/8-symmetrical/blob/main/symmio-core/contracts/facets/Account/AccountFacetImpl.sol#L53), partyB can also prevent this operation via chargeFundingRate.
Due to this issue, partyB can increase nonces of any partyA with little cost, causing some operations of partyA to fail (refer to the Vulnerability Detail section). This opens up the opportunity for partyB to turn the table.

## Recommendation
File: symmio-core\contracts\facets\PartyB\PartyBFacetImpl.sol
310:
function chargeFundingRate(
311:
address partyA,
312:
uint256[] memory quoteIds,
313:
int256[] memory rates,
314:
PairUpnlSig memory upnlSig
315:
) internal {
316:
LibMuon.verifyPairUpnl(upnlSig, msg.sender, partyA);
317:-
require(quoteIds.length == rates.length, "PartyBFacet: Length not match");
317:+
require(quoteIds.length > 0 && quoteIds.length == rates.length, "PartyBFacet: Length is 0 or Length not match");
