# [M] Emergency close might be blocked due to in-

## Summary
Severity: Medium
Contest weight: 0.4633
Dataset id: 1750
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Emergency close might be blocked due to insufficient PartyA's allocated balance.
During urgent situations where emergency mode is activated, the positions need to be promptly closed to avoid negative events that could potentially lead to serious loss of funds (e.g. the protocol is compromised, and the attacker is planning to or has started draining funds from the protocols). However, if the emergency closure of positions is blocked or delayed due to the above-mentioned issue, it might lead to unrecoverable losses.
• Emergency close does not handle an edge case where PartyA has insufficient allocated balance
Internal pre-conditions
External pre-conditions
Attack Path
Assuming a similar scenario mentioned in the Symm IO v0.8.3 documentation.
Bob (Party A) has three open positions and zero allocated balance:
1. Position 1 with Rasa Hedger (Party B1):
• Unrealized Profit: $300
• Quote ID: 1
2. Position 2 with PerpsHub Hedger (Party B2):
• Unrealized Profit: $100
• Quote ID: 2
3. Position 3 with PerpsHub Hedger (Party B2):
• Unrealized Loss: $250
• Quote ID: 3
PartyB wants to emergency close Bob's Position 3 via the emergencyClosePosition function, which has an unrealized loss of $250. However, since Bob has zero allocated balance, the loss in Position 3 cannot cover this loss upon closing, and an attempt to emergency close will revert.
main/protocol-core/contracts/facets/PartyBPositionActions/PartyBPositionActionsFacetImpl.sol#L99
File: PartyBPositionActionsFacetImpl.sol
99:
function emergencyClosePosition(uint256 quoteId, PairUpnlAndPriceSig memory upnlSig) internal {
100:
AccountStorage.Layout storage accountLayout = AccountStorage.layout();
101:
Quote storage quote = QuoteStorage.layout().quotes[quoteId];
102:
Symbol memory symbol = SymbolStorage.layout().symbols[quote.symbolId];
103:
require(
104:
GlobalAppStorage.layout().emergencyMode ||
GlobalAppStorage.layout().partyBEmergencyStatus[quote.partyB] ||
!symbol.isValid,
105:
"PartyBFacet: Operation not allowed. Either emergency mode must be active, party B must be in emergency status, or the symbol must be delisted"
106:
);
107:
require(quote.quoteStatus == QuoteStatus.OPENED || quote.quoteStatus == QuoteStatus.CLOSE_PENDING, "PartyBFacet: Invalid state");
108:
LibMuonPartyB.verifyPairUpnlAndPrice(upnlSig, quote.partyB, quote.partyA, quote.symbolId);
109:
uint256 filledAmount = LibQuote.quoteOpenAmount(quote);
110:
quote.quantityToClose = filledAmount;
111:
quote.requestedClosePrice = upnlSig.price;
112:
require(
113:
LibAccount.partyAAvailableBalanceForLiquidation(upnlSig.upnlPartyA, accountLayout.allocatedBalances[quote.partyA], quote.partyA) >= 0,
114:
"PartyBFacet: PartyA is insolvent"
115:
);
116:
require(
117:
LibAccount.partyBAvailableBalanceForLiquidation(upnlSig.upnlPartyB, quote.partyB, quote.partyA) >= 0,
118:
"PartyBFacet: PartyB should be solvent"
119:
);
120:
accountLayout.partyBNonces[quote.partyB][quote.partyA] += 1;
121:
accountLayout.partyANonces[quote.partyA] += 1;
122:
LibQuote.closeQuote(quote, filledAmount, upnlSig.price);
123:
}
During urgent situations where emergency mode is activated, the positions need to be promptly closed to avoid negative events that could potentially lead to serious loss of funds (e.g. the protocol is compromised, and the attacker is planning to or has started draining funds from the protocols). However, if the emergency closure of positions is blocked or delayed due to the above-mentioned issue, it might lead to unrecoverable losses.
```

## Recommendation
Consider implementing the settleUpnl function within the emergencyClosePosition function so that PartyB can proceed to settle PartyA's open positions to ensure that PartyA's allocated balance will have sufficient balance to allow the position to be emergency closed.
