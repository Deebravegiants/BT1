# [H] Users can bypass shareUnlockTime

## Summary
Severity: High
Contest weight: 0.7761
Dataset id: 9192
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When users call depositAndBridge, it will immediately transfer the token to the vault, then users will receive the minted shares and bridge it to the destination chain.
```solidity
function depositAndBridge(
    ERC20 depositAsset,
    uint256 depositAmount,
    uint256 minimumMint,
    BridgeData calldata data
) external payable {
    uint shareAmount = _erc20Deposit(depositAsset, depositAmount, minimumMint, msg.sender);
    bridge(shareAmount, data);
}
```
On the destination chain, it will then mint the shares to the destination receiver.
```solidity
function _lzReceive(
    Origin calldata _origin,
    bytes32 _guid,
    bytes calldata payload,
    address, // Executor address as specified by the OApp.
    bytes calldata // Any extra data or options to trigger on receipt.
) internal override {
    // @audit - should call _afterPublicDeposit if it from depositAndBridge
    // Decode the payload to get the message
    (uint256 shareAmount, address receiver) = abi.decode(payload, (uint256, address));
    vault.enter(address(0), ERC20(address(0)), 0, receiver, shareAmount);
}

function receiveBridgeMessage(address receiver, uint256 shareMintAmount) external {
    if(msg.sender != address(messenger)){
        revert CrossChainOPTellerWithMultiAssetSupport_OnlyMessenger();
    }
    if(messenger.xDomainMessageSender() != peer){
        revert CrossChainOPTellerWithMultiAssetSupport_OnlyPeerAsSender();
    }
    vault.enter(address(0), ERC20(address(0)), 0, receiver, shareMintAmount);
}
```
This operation can be abused if the bridging time (from source to destination) is less than the shareLockPeriod. Users could make their shares transferable sooner than the shareLockPeriod.

## Recommendation
Consider passing additional data or flag in the cross-chain operation, if it is called from depositAndBridge, consider calling _afterPublicDeposit for the receiver in the destination chain.
