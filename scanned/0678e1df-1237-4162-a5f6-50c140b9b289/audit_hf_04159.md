# [M] `_internalRemoteTransferSendPacket

## Summary
Severity: Medium
Contest weight: 0.5745
Dataset id: 20786
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _internalRemoteTransferSendPacket(
    address _srcChainSender,
    LZSendParam memory _lzSendParam,
    bytes memory _composeMsg
) internal returns (MessagingReceipt memory msgReceipt, OFTReceipt memory oftReceipt) {
    ...
    // If the srcChain amount request is bigger than the debited one, overwrite the amount to credit with the amount debited and send the difference back to the user.
    if (_lzSendParam.sendParam.amountLD > amountDebitedLD_) {
        // Overwrite the amount to credit with the amount debited
        _lzSendParam.sendParam.amountLD = amountDebitedLD_;
        _lzSendParam.sendParam.minAmountLD = amountDebitedLD_;
        // Send the difference back to the user
        _transfer(address(this), _srcChainSender, _lzSendParam.sendParam.amountLD - amountDebitedLD_);
    }
```
The above code, first modify `_lzSendParam.sendParam.amountLD = amountDebitedLD_` Then call `_transfer(address(this), _srcChainSender, _lzSendParam.sendParam.amountLD - amountDebitedLD_);`. This way the difference is always `0`.

Correctly `transfer()` the difference first, and then modify `_lzSendParam.sendParam.amountLD`.

## Recommendation
```solidity
function _internalRemoteTransferSendPacket(
    address _srcChainSender,
    LZSendParam memory _lzSendParam,
    bytes memory _composeMsg
) internal returns (MessagingReceipt memory msgReceipt, OFTReceipt memory oftReceipt) {
    ...
    // If the srcChain amount request is bigger than the debited one, overwrite the amount to credit with the amount debited and send the difference back to the user.
    if (_lzSendParam.sendParam.amountLD > amountDebitedLD_) {
        _transfer(address(this), _srcChainSender, _lzSendParam.sendParam.amountLD - amountDebitedLD_);
        // Overwrite the amount to credit with the amount debited
        _lzSendParam.sendParam.amountLD = amountDebitedLD_;
        _lzSendParam.sendParam.minAmountLD = amountDebitedLD_;
        // Send the difference back to the user
    }
```
