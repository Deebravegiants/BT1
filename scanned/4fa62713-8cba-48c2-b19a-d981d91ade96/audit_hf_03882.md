# [H] Accounting error in PartyB's pending locked

## Summary
Severity: High
Contest weight: 0.7892
Dataset id: 20165
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Accounting error in the PartyB's pending locked balance during the partial filling of a position could lead to a loss of assets for PartyB.
ontracts/facets/PartyB/PartyBFacet.sol#L150
File: PartyBFacetImpl.sol
```solidity
function openPosition(
    uint256 quoteId,
    uint256 filledAmount,
    uint256 openedPrice,
    PairUpnlAndPriceSig memory upnlSig
) internal returns (uint256 currentId) {
    // ...SNIP...
    LibQuote.removeFromPendingQuotes(quote);
    // ...SNIP...
    quoteLayout.quoteIdsOf[quote.partyA].push(currentId);
    // ...SNIP...
    } else {
        accountLayout.pendingLockedBalances[quote.partyA].sub(filledLockedValues);
        accountLayout.partyBPendingLockedBalances[quote.partyB][quote.partyA].sub(
            filledLockedValues
        );
    }
```
() Parameter Description ()
quotecurrent Current quote (Quote ID = 1)
quotenew Newly created quote (Quote ID = 2) due to partially filling
lockedValuetotal 100 USD. The locked values of quotecurrent
lockedValuefilled 30 USD. lockedValuefilled = lockedValuetotal × filledAmount / quote.quantity
lockedValueunfilled 70 USD. lockedValueunfilled = lockedValuetotal - lockedValuefilled
pendingLockedBalancea 100 USD. PartyA's pending locked balance
pendingLockedBalanceb 100 USD. PartyB's pending locked balance
pendingQuotesa PartyA's pending quotes. pendingQuotesa = [quotecurrent]
pendingQuotesb PartyB's pending quotes. pendingQuotesb = [quotecurrent]
()
Assume the following states before the execution of the openPosition function:
• pendingQuotesa = [quotecurrent]
• pendingQuotesb = [quotecurrent]
• pendingLockedBalancea = 100 USD
• pendingLockedBalanceb = 100 USD
When the openPosition function is executed, quotecurrent will be removed from pendingQuotesa and pendingQuotesb in Line 156.
If the position is partially filled, quotecurrent will be filled, and quotenew will be created with the unfilled amount (lockedValueunfilled). The quotenew is automatically added to PartyA's pending quote list in Line 225.
The states at this point are as follows:
• pendingQuotesa = [quotenew]
• pendingQuotesb = []
• pendingLockedBalancea = 100 USD
• pendingLockedBalanceb = 100 USD
Line 238 removes the balance already filled (lockedValuefilled) from pendingLockedBalancea. The unfilled balance (lockedValueunfilled) does not need to be removed from pendingLockedBalancea because it is now the balance of quotenew that belong to PartyA. The value in pendingLockedBalancea is correct.
The states at this point are as follows:
• pendingQuotesa = [quotenew]
• pendingQuotesb = []
• pendingLockedBalancea = 70 USD
• pendingLockedBalanceb = 100 USD
In Line 239, the code removes the balance already filled (lockedValuefilled) from pendingLockedBalanceb.
The end state is as follows:
• pendingQuotesa = [quotenew]
• pendingQuotesb = []
• pendingLockedBalancea = 70 USD
• pendingLockedBalanceb = 70 USD
As shown above, the value of pendingLockedBalanceb is incorrect. Even though PartyB has no pending quote, 70 USD is still locked in the pending balance.
1) quotecurrent has already been removed from pendingQuotesb in Line 156
2) quotenew is not automatically added to pendingQuotesb. When quotenew is created, it is not automatically locked to PartyB.
3) pendingQuotesb is empty
As such, lockedValuetotal should be removed from the pendingLockedBalanceb instead of only lockedValuefilled.
Every time PartyB partially fill a position, their pendingLockedBalanceb will silently increase and become inflated. The pending locked balance plays a key role in the protocol's accounting system. Thus, an error in the accounting breaks many of the computations and invariants of the protocol.
For instance, it is used to compute the available balance of an account in partyBAvailableForQuote function. Assuming that the allocated balance remains the same. If the pending locked balance increases silently due to the bug, the available balance returned from the partyBAvailableForQuote function will decrease. Eventually, it will "consume" all the allocated balance, and there will be no available funds left for PartyB to open new positions or to deallocate+withdraw funds. Thus, leading to loss of assets for PartyB.

## Recommendation
Update the affected function to remove lockedValuetotal from the pendingLockedBalanceb instead of only lockedValuefilled.
```solidity
accountLayout.pendingLockedBalances[quote.partyA].sub(filledLockedValues);
accountLayout.partyBPendingLockedBalances[quote.partyB][quote.partyA].sub(
    quote.lockedValues
);
```
