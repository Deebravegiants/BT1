# [M] ProxyLedger operations will always revert due

## Summary
Severity: Medium
Contest weight: 0.6974
Dataset id: 22973
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function vaultSendToLedger(OCCVaultMessage memory message) internal {
    if (message.tokenAmount > 0) {
        address erc20TokenAddr = IOFT(orderTokenOft).token();
        IERC20(erc20TokenAddr).safeTransferFrom(message.sender, address(this), message.tokenAmount);
        if (IOFT(orderTokenOft).approvalRequired()) {
            IERC20(erc20TokenAddr).approve(address(orderTokenOft), message.tokenAmount);
        }
    }
    SendParam memory sendParam = buildOCCVaultMsg(message);
    MessagingFee memory msgFee = MessagingFee(msg.value, 0);
    uint256 lzFee = msg.value - payloadType2BackwardFee[message.payloadType];
    (_msgReceipt, _oftReceipt) = IOFT(orderTokenOft).send{value: lzFee}(sendParam, msgFee, msg.sender);
    chainedEventId += 1;
}
```
The ProxyLedger contract operations such as claimReward, stakeOrder, and sendUserRequest on the destination chain utilize the LayerZero protocol. However, discrepancies in the fee mentioned in msg.value and the msgFee parameter when calling _lzSend() will cause the transaction to revert. The vulnerability lies in the vaultSendToLedger function, which erroneously transfers the payloadType2BackwardFee[message.payloadType] to LayerZero along with the LayerZero fee. File: omnichain-ledger/contracts/lib/OCCManager.sol The vaultSendToLedger function transfers lzFee as msg.value but sets msgFee as the fee parameter to IOFT(orderTokenOft).send(). File: oft-token/contracts/layerzerolabs/lz-evm-oapp-v2/contracts/oft/OFTCoreUpgradeable.sol
```solidity
msgReceipt = _lzSend(_sendParam.dstEid, message, options, _fee, _refundAddress);
```
Then send() calls _lzSend() to interact with the LayerZero EndpointV2.send(). Subsequently, _lzSend() calls _payNative() to pay the native fee associated with the message. File: oft-token/contracts/layerzerolabs/lz-evm-oapp-v2/contracts/oapp/OAppSenderUpgradeable.sol
```solidity
uint256 messageValue = _payNative(_fee.nativeFee);
```
Here, the transaction reverts if msg.value is not equal to _nativeFee, meaning the vaultSendToLedger function transfers lzFee as msg.value and msgFee (sum of lzFee + payloadType2BackwardFee[message.payloadType]). Therefore, the transaction will revert due to this check.
```solidity
function _payNative(uint256 _nativeFee) internal virtual returns (uint256 nativeFee) {
    return _nativeFee;
}
```
claimReward, stakeOrder, and sendUserRequest transactions will always revert due to transferring a fee (as msg.value) that is greater than what LayerZero requires (mentioned in the parameters as msgFee) to process the transaction.

## Recommendation
```solidity
function vaultSendToLedger(OCCVaultMessage memory message) internal {
    if (message.tokenAmount > 0) {
        address erc20TokenAddr = IOFT(orderTokenOft).token();
        IERC20(erc20TokenAddr).safeTransferFrom(message.sender, address(this), message.tokenAmount);
        if (IOFT(orderTokenOft).approvalRequired()) {
            IERC20(erc20TokenAddr).approve(address(orderTokenOft), message.tokenAmount);
        }
    }
    SendParam memory sendParam = buildOCCVaultMsg(message);
    uint256 lzFee = msg.value - payloadType2BackwardFee[message.payloadType];
    MessagingFee memory msgFee = MessagingFee(lzFee, 0);
    (_msgReceipt, _oftReceipt) = IOFT(orderTokenOft).send{value: lzFee}(sendParam, msgFee, msg.sender);
    chainedEventId += 1;
}
```
