# [H] InfernalRiftBelow.thresholdCross

## Summary
Severity: High
Contest weight: 0.8830
Dataset id: 23213
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
InfernalRiftBelow.thresholdCross verify the wrong msg.sender, thresholdCross will fail to be called, resulting in the loss of user assets.
thresholdCross determines whether msg.sender is expectedAliasedSender:
```solidity
address expectedAliasedSender = address(uint160(INFERNAL_RIFT_ABOVE) +
uint160(0x1111000000000000000000000000000000001111));
// Ensure the msg.sender is the aliased address of {InfernalRiftAbove}
if (msg.sender != expectedAliasedSender) {
    revert CrossChainSenderIsNotRiftAbove();
}
```
but in fact the function caller should be RELAYER_ADDRESS, In sudoswap, crossTheThreshold check whether msg.sender is RELAYER_ADDRESS: https://github.com/sudoswap/InfernalRift/blob/7696827b3221929b3fa563692bd4c5d73b20528e/src/InfernalRiftBelow.sol#L56
L1 across chain message through the PORTAL.depositTransaction, rather than L1_CROSS_DOMAIN_MESSENGER.
To avoid confusion, use in L1 should all L1_CROSS_DOMAIN_MESSENGER.sendMessage to send messages across the chain, avoid the use of low level PORTAL.depositTransaction function.
```solidity
function crossTheThreshold(ThresholdCrossParams memory params) external payable {
    // Send package off to the portal
    PORTAL.depositTransaction{value: msg.value}(
        INFERNAL_RIFT_BELOW,
        0,
        params.gasLimit,
        false,
        abi.encodeCall(InfernalRiftBelow.thresholdCross, (package,
        params.recipient))
    );
    emit BridgeStarted(address(INFERNAL_RIFT_BELOW), package, params.recipient);
}
```
When transferring nft across chains, thresholdCross cannot be called in L2, resulting in loss of user assets.

## Recommendation
```solidity
// Validate caller is cross-chain
if (msg.sender != RELAYER_ADDRESS) { //or L2_CROSS_DOMAIN_MESSENGER
    revert NotCrossDomainMessenger();
}
// Validate caller comes from {InfernalRiftBelow}
if (ICrossDomainMessenger(msg.sender).xDomainMessageSender() != InfernalRiftAbove) {
    revert CrossChainSenderIsNotRiftBelow();
}
```
