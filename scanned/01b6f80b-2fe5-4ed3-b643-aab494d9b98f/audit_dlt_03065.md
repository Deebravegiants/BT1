# [M] TOFT `exerciseOption` fails due to not passing `msg.value` properly

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1248
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapiocaz-audit/blob/master/contracts/tOFT/BaseTOFT.sol#L127-L146
https://github.com/Tapioca-DAO/tapiocaz-audit/blob/master/contracts/tOFT/BaseTOFT.sol#L536-L550


# Vulnerability details

## Impact

Packet type `PT_TAP_EXERCISE` always reverts due to not passing properly the `msg.value` to the final destination contract.
When first sent out it will revert and be stored inside `failedMessages` and the user is not able to retry the message.
The user losses gas and `TOFT` tokens by using this function.

### Layer Zero message delivery
LayerZero is a messaging protocol that enables the delivery of payload from chainA to chainB. 
The sender specifies and pays for the destination gas and has the option of airdropping native gas tokens into an address on the destination chain. This is done through [relayer params](https://layerzero.gitbook.io/docs/evm-guides/advanced/relayer-adapter-parameters).
The Relayer invokes the [validateTransactionProofV2](https://github.com/LayerZero-Labs/LayerZero/blob/main/contracts/RelayerV2.sol#L164-L171) function on the destination chain to deliver the payload.
The airdropped value is not part of the `msg.value` but is delivered as `address(this).balance` on the destination contract. Also, the [`validateTransactionProofV2`](https://github.com/LayerZero-Labs/LayerZero/blob/main/contracts/RelayerV2.sol#L164-L171) function doesn't revert if airdropped tokens are not sent to the destination contract. It just emits an event, so the assumption always has to be that nothing is airdropped in the worst case.
```solidity
(bool sent, ) = _to.call{value: msg.value}("");
//require(sent, "Relayer: failed to send ether");
if (!sent) {
    emit ValueTransferFailed(_to, msg.value);
}
```

## Proof of Concept

The flow of the issue is the following:

1. User invokes [exerciseOption](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/master/contracts/tOFT/BaseTOFT.sol#L127) function and is allowed to pass on a bunch of parameters which are not validated.
The only thing which is validated is does he have enough TOFT tokens, which are being burned and the packetType is `PT_TAP_EXERCISE` and he cannot airdrop any native tokens since [adapterParamsV1](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/master/contracts/tOFT/modules/BaseTOFTOptionsModule.sol#L97-L98) are enforced. 
2. When this message is delivered to the destination chain, the first step is [decoding the params](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/master/contracts/tOFT/modules/BaseTOFTOptionsModule.sol#L160-L175).
3. If one of the decoded params `tapSendData.withdrawOnAnotherChain` is true after exercising the option the tapOFT tokens are tried to be [sent out](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/master/contracts/tOFT/modules/BaseTOFTOptionsModule.sol#L240-L253) to another chain. The problem is that the `sendFrom` is missing `{value: address(this.balance)` and the transaction reverts.
4. if we take a look at the implementation of the `sendFrom` function inside the [BaseOFTV2](https://github.com/Tapioca-DAO/tapioca-sdk-audit/blob/90d1e8a16ebe278e86720bc9b69596f74320e749/src/contracts/token/oft/v2/BaseOFTV2.sol#L17-L19) and the underlying [_send](https://github.com/Tapioca-DAO/tapioca-sdk-audit/blob/90d1e8a16ebe278e86720bc9b69596f74320e749/src/contracts/token/oft/v2/OFTCoreV2.sol#L94-L105) function in `OFTCoreV2`.
We can see that the `_lzSend` relies on the `msg.value`. However, in this case `msg.value` is always 0.
5. Even if the sending side allowed to airdrop some native tokens, again in my explanation of the [Layer Zero message delivery](#layer-zero-message-delivery) the airdropped tokens are always airdropped as a balance of the contract, so the issue needs to be addressed in multiple places in the code.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1248_
