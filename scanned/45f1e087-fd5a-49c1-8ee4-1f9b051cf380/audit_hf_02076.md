# [H] Possible Signature Verification Bypass in Messenger

## Summary
Severity: High
Contest weight: 0.6022
Dataset id: 11755
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Bool Network protocol has a core Messenger contract that is responsible for facilitating cross-chain communication across networks. In the process of verifying received messages from Bool Network, we notice the verification logic may be bypassed. In the following, we show the implementation of the related receiveFromBool() routine. It has a rather straightforward logic in validating the received message and invoking the receiveFromMessenger() function on the intended anchor. And the validation is performed in an internal helper _verifySignature(). Unfortunately, the helper relies on the given user input and the baseline comparison also depends on external input, which is not trustworthy either. As a result, the current validation can be readily bypassed. A bypassed cross-chain message can be crafted to completely mess up the consumer's state, potentially draining funds in the pool.
```solidity
function receiveFromBool(
    Message memory message,
    bytes calldata signature
) external override nonReentrant {
    // First and foremost, check the replay attack
    (uint32 srcChainId, , uint192 nonce) = _unpackAndCheckTxIdentification(
        message.txUniqueIdentification
    );
    // Check if the signature is valid
    if (!_verifySignature(message, signature)) revert INVALID_SIGNATURE();
    address dstAnchor = message.dstAnchor.fromBytes32ToAddress();
    IAnchor.MessageStatus
```

## Recommendation
Improve the above routine to ensure the signature validation is securely performed without being bypassed.
