# [C] 5.1.1 msg.senderhas to be un-aliased inL2BlastBridge.finalizeBridgeETHDirect().

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk

**Context:** L2BlastBridge.sol#L

**Description:** L2BlastBridge.finalizeBridgeETHDirect()checks thatmsg.senderisL1BlastBridge:

```
require(msg.sender == address(OTHER_BRIDGE), "StandardBridge: function can only be called from the
,! other bridge");
```
However, since the function is called directly as a L1!L2 transaction initiated byL1BlastBridge, which is a
contract,msg.senderwill actually be the aliased address ofL1BlastBridge. OTHER_BRIDGEis the un-aliased
address ofL1BlastBridgeas other functions inL2BlastBridgeuse it, such as_initiateBridgeETH().

As such, this check will always revert, thus users who deposit stETH inL1BlastBridgewill not receive ETH on L2.

**Recommendation:** Un-aliasmsg.senderin the check as such:

- require(msg.sender == address(OTHER_BRIDGE), "StandardBridge: function can only be called from the
    ,! other bridge");
+ require(AddressAliasHelper.undoL1ToL2Alias(msg.sender) == address(OTHER_BRIDGE), "StandardBridge:
    ,! function can only be called from the other bridge");
