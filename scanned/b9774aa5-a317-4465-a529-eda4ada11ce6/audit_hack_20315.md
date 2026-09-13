# [H] 5.1.2 CelerIMFacetincorrectly setsRelayerCelerIMas receiver

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** CelerIMFacet.sol#L171-L
**Description:** When assigning abytes memoryvariable to a new variable, the new variable points to the same
memory location. Changing any one variable updates the other variable. Here is a PoC as a foundry test
function testCopy() public {
Pp memory x = Pp({
a: 2,
b: address(2)
});
Pp memory y = x;
y.b = address(1);
assertEq(x.b, y.b);
}

Thus, whenCelerIMFacet._startBridge()updatesbridgeDataAdjusted.receiver,_bridgeData.receiveris
implicitly updated too. This makes the receiver on the destination chain to be the relayer address.
// case'yes': bridge + dest call - send to relayer
ILiFi.BridgeData memory bridgeDataAdjusted = _bridgeData;
bridgeDataAdjusted.receiver = address(relayer);
(bytes32 transferId, address bridgeAddress) = relayer
.sendTokenTransfer{ value: msgValue }(bridgeDataAdjusted, _celerIMData);
// call message bus via relayer incl messageBusFee
relayer.forwardSendMessageWithTransfer{value: _celerIMData.messageBusFee}(
_bridgeData.receiver,
uint64(_bridgeData.destinationChainId),
bridgeAddress,
transferId,
_celerIMData.callData
);

**Recommendation:** RemovebridgeDataAdjustedand work with_bridgeDataas follows:
// case'yes': bridge + dest call - send to relayer
-ILiFi.BridgeData memory bridgeDataAdjusted = _bridgeData;
-bridgeDataAdjusted.receiver = address(relayer);
+address receiver = _bridgeData.receiver;
+_bridgeData.receiver = address(relayer);
(bytes32 transferId, address bridgeAddress) = relayer
-.sendTokenTransfer{ value: msgValue }(bridgeDataAdjusted, _celerIMData);
+.sendTokenTransfer{ value: msgValue }(_bridgeData, _celerIMData);
// call message bus via relayer incl messageBusFee
relayer.forwardSendMessageWithTransfer{value: _celerIMData.messageBusFee}(

- _bridgeData.receiver
+ receiver,
    uint64(_bridgeData.destinationChainId),
    bridgeAddress,
    transferId,
    _celerIMData.callData
);
+_bridgeData.receiver = receiver;

**LiFi:** Fixed in PR 252.
**Spearbit:** Verified.
