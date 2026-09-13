# [C] 5.1.1 Lack oftransferIdVerification Allows an Attacker to Front-Run Bridge Transfers

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** NomadFacet.sol#L99-L149, BridgeRouter.sol#L176-L199, BridgeRouter.sol#L347-L
**Description:** TheonReceive()function does not verify the integrity oftransferIdagainst all other parameters.
Although theonlyBridgeRoutermodifier checks that the call originates from another BridgeRouter (assuming a
correct configuration of the whitelist) to theonReceive()function, it does not check that the call originates from
another Connext Diamond.
Therefore, allowing anyone to send arbitrary data toBridgeRouter.sendToHook(), which is later interpreted as
thetransferIdon Connext’sNomadFacet.solcontract.
This can be abused by a front-running attack as described in the following scenario:

- Alice is a bridge user and makes an honest call to transfer funds over to the destination chain.
- Bob does not make a transfer but instead calls thesendToHook()function with the same_extraDatabut
    passes an_amountof1 wei.
- Both Alice and Bob have their tokens debited on the source chain and must wait for the Nomad protocol to
    optimistically verify incomingTransferToHookmessages.
- Once the messages have been replicated onto the destination chain, Bob processes the message before
    Alice, causingonReceive()to be called on the sametransferId.
- However, because_amountis not verified against thetransferId, Alice receives significantly less tokens
    and thes.reconciledTransfersmapping marks the transfer as reconciled. Hence, Alice has effectively lost
    all her tokens during an attempt to bridge them.
function onReceive(
uint32,// _origin, not used
uint32,// _tokenDomain, not used
bytes32,// _tokenAddress, of canonical token, not used
address _localToken,
uint256 _amount,
bytes memory _extraData
) external onlyBridgeRouter {
bytes32 transferId = bytes32(_extraData);
// Ensure the transaction has not already been handled (i.e. previously reconciled).
if (s.reconciledTransfers[transferId]) {
revert NomadFacet__reconcile_alreadyReconciled();
}
// Mark the transfer as reconciled.
s.reconciledTransfers[transferId] = true;

Note: the same issues exists with_localToken. As a result a malicious user could perform the same attack by
using a malicious token contract and transferring the same amount of tokens in the call tosendToHook().
**Recommendation:** Verify that the call originates from the Connext Diamond on the originator chain. In function
reconcile()verify thattransferIdis indeed a hash of the other parameters.
**Connext:** Solved in PR 1630 and PR 1678.
**Spearbit:** Note: TheBridgeRouterand the interface to it has changed quite a lot during and after this audit. As
it was out of scope for this audit it is also important to conduct a separate review of that particular code, including
the interface to Connext.
**Connext:** An extra audit forBridgeRouteris underway.


**Spearbit:** Acknowledged.
