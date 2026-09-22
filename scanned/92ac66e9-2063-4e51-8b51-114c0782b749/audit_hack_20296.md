# [H] **5.1.3** PolygonSpokeConnector **or** PolygonHubConnector **can get compromised and DoSed if an address(0)

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
is passed to their constructor for** _mirrorConnector

**Severity:** High Risk
**Context:**

- FxBaseChildTunnel.sol#L38-L
- FxBaseRootTunnel.sol#L58-L
- Connector.sol#L119-L
- PolygonSpokeConnector.sol#L78-L
- PolygonHubConnector.sol#L51-L
**Description:** PolygonSpokeConnector(PolygonHubConnector) inherits fromSpokeConnector(HubConnector)
andFxBaseChildTunnel(FxBaseRootTunnel). WhenPolygonSpokeConnector(PolygonHubConnector) gets de-
ployed and its constructor is called, if_mirrorConnector == address(0)then setting themirrorConnectorstor-
age variable is skipped:

```
// File: Connector.sol#L118-L
if (_mirrorConnector != address(0)) {
_setMirrorConnector(_mirrorConnector);
}
```
Now since thesetFxRootTunnel(setFxChildTunnel) is an unprotected endpoint that is not overridden by
PolygonSpokeConnector (PolygonHubConnector) anyone can call it and assign their own fxRootTunnel
(fxChildTunnel) address (note,fxRootTunnel(fxChildTunnel) is supposed to correspond tomirrorConnector
on the destination domain).
Note that the require statement in setFxRootTunnel (setFxChildTunnel) only allows fxRootTunnel
(fxChildTunnel) to be set once (non-zero address value) so afterward even the owner cannot update this value.
If at some later time the owner tries to callsetMirrorConnectorto assign themirrorConnector, since_setMir-
rorConnectoris overridden byPolygonSpokeConnector(PolygonHubConnector) the following will try to execute:


```
// File: PolygonSpokeConnector.sol#L78-L
function _setMirrorConnector(address _mirrorConnector) internal override {
super._setMirrorConnector(_mirrorConnector);
setFxRootTunnel(_mirrorConnector);
}
```
Or forPolygonHubConnector:
// File: PolygonHubConnector.sol#L51-L
function _setMirrorConnector(address _mirrorConnector) internal override {
super._setMirrorConnector(_mirrorConnector);
setFxChildTunnel(_mirrorConnector);
}

But this will revert sincefxRootTunnel(fxChildTunnel) is already set. Thus if the owner ofPolygonSpokeConnec-
tor(PolygonHubConnector) does not provide a non-zero address value formirrorConnectorupon deployment, a
malicious actor can setfxRootTunnelwhich will cause:

1. Rerouting of messages from Polygon to Ethereum to an address decided by the malicious actor (or vice
    versa forPolygonHubConnector).
2. DoSing thesetMirrorConnectorandsetFxRootTunnel(fxChildTunnel) endpoints for the owner.
**Recommendation:** Make sure either a non-zero address value of_mirrorConnectoris submitted/enforced
in PolygonSpokeConnector's (PolygonHubConnector) constructor or override the setFxRootTunnel
(setFxChildTunnel) endpoint to disallow a call from a random user, enabling a select few privileged users to be
able to call.
**Connext:** Only owner can update now. Solved in PR 2387.
**Spearbit:** Verified.
