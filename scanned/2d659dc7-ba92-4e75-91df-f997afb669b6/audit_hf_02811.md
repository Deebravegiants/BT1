# [H] Users can break the lz communication

## Summary
Severity: High
Contest weight: 0.7873
Dataset id: 15495
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LayerZeroImpl contract uses the NonBlockingLzApp from the LZ SDK to store all failed messages for future retries:
```solidity
function _blockingLzReceive(
    uint16 _srcChainId,
    bytes memory _srcAddress,
    uint64 _nonce,
    bytes memory payload
) internal {
    (bool success, bytes memory reason) = address(this).excessivelySafeCall(
        gasleft(),
        abi.encodeWithSelector(
            this.nonblockingLzReceive.selector,
            _srcChainId,
            _srcAddress,
            _nonce,
            payload
        )
    );
    if (!success) {
        _storeFailedMessage(_srcChainId, _srcAddress, _nonce, payload, reason);
    }
}
```
The function uses up to gasleft() gas and reads up to 150 bytes of returndata using excessivelySafeCall(). Due to the 63/64 rule, only 1/64 of the remaining gas is left for storing the failed message if nonblockingLzReceive() uses all its allocated gas. LayerZeroImpl forwards 600k gas to the endpoint:
```solidity
endpoint.send{value: msg.value}(
    _dstChainId,
    abi.encodePacked(dstCommLayer[uint16(_dstChainId)], address(this)),
    _payload,
    payable(refundAd),
    address(0x0),
    abi.encodePacked(uint16(1), uint256(600000)) // 600k
)
```
If all 63/64 gas is used, only ~9000 gas remains for storing the failed message, which is insufficient since a single zero to non-zero SSTORE costs 22.1k gas. This results in a revert in the Endpoint try/catch handling.
```solidity
try ILayerZeroReceiver(_dstAddress).lzReceive{gas: _gasLimit}(
    _srcChainId,
    _srcAddress,
    _nonce,
    _payload
) {
    // success, do nothing, end of the message delivery
} catch (bytes memory reason) {
    // revert nonce if any uncaught errors/exceptions if the ua chooses
    // the blocking mode
    storedPayload[_srcChainId][_srcAddress] = StoredPayload(uint64(_payload.length), _dstAddress, keccak256(_payload));
    emit PayloadStored(_srcChainId, _srcAddress, _dstAddress, _nonce, _payload, reason);
}
```
That is the portion that stores the payload and blocks the channel. Since gas is capped to gasLimit here, there's no risk of not leaving enough gas to store the failure in storedPayload, the Relayer is just expected to provide a small extra buffer for running the logic before and after lzReceive(). A malicious user can exploit this by wasting all the allocated gas using the onERC721Received(). Bob is a smart contract with a malicious code in his onERC721Received() that will waste all the allocated gas. Bob calls crossChainBuy() to buy DAO tokens, triggering the following call stack: commLayer.sendMsg() → endpoint.send() → commLayer.lzReceive() → lzReceive() calls _nonblockingLzReceive() → factory.crossChainMint() → crossChainMint() will make some sanity checks and then call: dao.mintToken() → _safeMint() → onERC721Received(). Bob onERC721Received() hook will waste the entire allocated gas, causing _blockingLzReceive() to fail and attempts to store the failed message with insufficient gas. The revert bubbles up to the Endpoint try/catch handling, resulting in a blocked pathway.

## Recommendation
A simple and effective solution is to use mint instead of safeMint. Make sure to document this clearly: If to is a smart contract, it must implement {IERC721Receiver-onERC721Received} hook.
