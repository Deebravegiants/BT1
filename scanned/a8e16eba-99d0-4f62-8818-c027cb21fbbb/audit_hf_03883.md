# [H] Liquidation can be blocked by incrementing

## Summary
Severity: High
Contest weight: 0.7940
Dataset id: 20166
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious users could block liquidators from liquidating their accounts, which creates unfairness in the system and lead to a loss of profits to the counterparty.
Instance 1 - Blocking liquidation of PartyA
A liquidatable PartyA can block liquidators from liquidating its account.
ontracts/facets/liquidation/LiquidationFacetImpl.sol#L20
File: LiquidationFacetImpl.sol
```solidity
function liquidatePartyA(address partyA, SingleUpnlSig memory upnlSig) internal {
    MAStorage.Layout storage maLayout = MAStorage.layout();
    LibMuon.verifyPartyAUpnl(upnlSig, partyA);
    int256 availableBalance = LibAccount.partyAAvailableBalanceForLiquidation(
        upnlSig.upnl,
        partyA
    );
    require(availableBalance < 0, "LiquidationFacet: PartyA is solvent");
    maLayout.liquidationStatus[partyA] = true;
    maLayout.liquidationTimestamp[partyA] = upnlSig.timestamp;
    AccountStorage.layout().liquidators[partyA].push(msg.sender);
}
```
Within the liquidatePartyA function, it calls the LibMuon.verifyPartyAUpnl function.
ontracts/libraries/LibMuon.sol#L87
File: LibMuon.sol
```solidity
function verifyPartyAUpnl(SingleUpnlSig memory upnlSig, address partyA) internal view {
    MuonStorage.Layout storage muonLayout = MuonStorage.layout();
    require(
        block.timestamp <= upnlSig.timestamp + muonLayout.upnlValidTime,
        "LibMuon: Expired signature"
    );
    bytes32 hash = keccak256(
        abi.encodePacked(
            muonLayout.muonAppId,
            upnlSig.reqId,
            address(this),
            partyA,
            AccountStorage.layout().partyANonces[partyA],
            upnlSig.upnl,
            upnlSig.timestamp,
            getChainId()
        )
    );
    verifyTSSAndGateway(hash, upnlSig.sigs, upnlSig.gatewaySignature);
}
```
The verifyPartyAUpnl function will take the current nonce of PartyA (AccountStorage.layout().partyANonces[partyA]) to build the hash needed for verification.
When the PartyA becomes liquidatable or near to becoming liquidatable, it could start to monitor the mempool for any transaction that attempts to liquidate their accounts. Whenever a liquidator submits a liquidatePartyA transaction to liquidate their accounts, they could front-run it and submit a transaction to increment their nonce. When the liquidator's transaction is executed, the on-chain PartyA's nonce will differ from the nonce in the signature, and the liquidation transaction will revert.
For those chains that do not have a public mempool, they can possibly choose to submit a transaction that increments their nonce in every block as long as it is economically feasible to obtain the same result.
Gas fees that PartyA spent might be cheap compared to the number of assets they will lose if their account is liquidated. Additionally, gas fees are cheap on L2 or side-chain (The protocol intended to support Arbitrum One, Arbitrum Nova, Fantom, Optimism, BNB chain, Polygon, Avalanche as per the contest details).
There are a number of methods for PartyA to increment their nonce, this includes but not limited to the following:
• Allocate or deallocate dust amount
• Lock and unlock dummy position
• Calls requestToClosePosition followed by requestToCancelCloseRequest immediately
Instance 2 - Blocking liquidation of PartyB
The same exploit can be used to block the liquidation of PartyB since the liquidatePartyB function also relies on the LibMuon.verifyPartyBUpnl, which uses the on-chain nonce of PartyB for signature verification.
ontracts/facets/liquidation/LiquidationFacetImpl.sol#L240
File: LiquidationFacetImpl.sol
```solidity
function liquidatePartyB(
    // ...SNIP...
    LibMuon.verifyPartyBUpnl(upnlSig, partyB, partyA);
```
PartyA can block their accounts from being liquidated by liquidators. With the ability to liquidate the insolvent PartyA, the unrealized profits of all PartyBs cannot be realized, and thus they will not be able to withdraw profits.
PartyA could also exploit this issue to block their account from being liquidated to:
• Wait for their positions to recover to reduce their losses
• Buy time to obtain funds elsewhere to inject into their accounts to bring the account back to a healthy level
Since this is a zero-sum game, the above-mentioned create unfairness to PartyB and reduce their profits.
The impact is the same for the blocking of PartyB liquidation.

## Recommendation
In most protocols, whether an account is liquidatable is determined on-chain, and this issue will not surface. However, the architecture of Symmetrical protocol relies on off-chain and on-chain components to determine if an account is liquidatable, which can introduce a number of race conditions such as the one mentioned in this.
Consider reviewing the impact of malicious users attempting to increment the nonce in order to block certain actions in the protocols since most functions rely on the fact that the on-chain nonce must be in sync with the signature's nonce and update the architecture/contracts of the protocol accordingly.
