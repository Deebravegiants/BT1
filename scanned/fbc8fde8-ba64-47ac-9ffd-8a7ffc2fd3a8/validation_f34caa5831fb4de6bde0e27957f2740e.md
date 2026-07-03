### Title
`updateSrcChainId` Transition Blocks In-Flight LayerZero Messages, Causing Stale Rate - (`contracts/cross-chain/CrossChainRateReceiver.sol`)

### Summary
When the owner calls `updateSrcChainId` to migrate to a new chain ID while a valid rate message from the old chain is already in the LayerZero delivery queue, `lzReceive` will revert on that in-flight message. In LayerZero v1 blocking mode this stores the payload and halts the channel. Because `CrossChainRateReceiver` exposes no function to call `forceResumeReceive` on the endpoint, the channel cannot be unblocked through the contract, and the rate update is permanently lost until a manual workaround is executed.

### Finding Description

`lzReceive` enforces a strict equality check against the current `srcChainId` state variable: [1](#0-0) 

`updateSrcChainId` atomically overwrites `srcChainId` with no transition window: [2](#0-1) 

LayerZero v1 delivers messages in order (blocking mode). If `lzReceive` reverts, the endpoint stores the payload and blocks the channel. The endpoint exposes `retryPayload` and `forceResumeReceive` to recover: [3](#0-2) [4](#0-3) 

`forceResumeReceive` on the endpoint requires `msg.sender` to be the UA (the receiver contract itself). `CrossChainRateReceiver` implements neither a wrapper for `forceResumeReceive` nor any other recovery path, so the owner cannot unblock the channel through the contract. [5](#0-4) 

### Impact Explanation
The receiver contract (`RSETHRateReceiver` / `AGETHRateReceiver`) holds a stale `rate` value. Any downstream pool or oracle that calls `getRate()` continues to use the pre-migration rate indefinitely until the channel is manually unblocked and a new rate message is delivered. This matches **Low: Contract fails to deliver promised returns, but doesn't lose value**. [6](#0-5) 

### Likelihood Explanation
Chain ID migrations are a realistic operational event (e.g., LayerZero endpoint upgrades, chain reconfigurations). The window between `updateRate()` on the provider and delivery on the receiver is non-zero (cross-chain latency). No special attacker is needed — the owner's own legitimate migration triggers the condition.

### Recommendation
1. Add a `forceResumeReceive` passthrough so the owner can unblock the channel:
   ```solidity
   function forceResumeReceive(uint16 _srcChainId, bytes calldata _srcAddress) external onlyOwner {
       ILayerZeroEndpoint(layerZeroEndpoint).forceResumeReceive(_srcChainId, _srcAddress);
   }
   ```
2. Alternatively, accept both old and new chain IDs during a configurable transition period before fully switching.

### Proof of Concept

```solidity
// 1. Deploy CrossChainRateReceiver with srcChainId = A
// 2. Provider sends updateRate() from chain A → message in-flight
// 3. Owner calls updateSrcChainId(B) → srcChainId = B
// 4. LayerZero endpoint delivers the in-flight message:
//    lzReceive(A, ...) → require(A == B) → REVERT
// 5. Endpoint stores payload; channel is blocked
// 6. getRate() still returns the old stale rate
// 7. No function on CrossChainRateReceiver can call
//    endpoint.forceResumeReceive(...) → channel stays blocked

// Assert: rate unchanged, channel blocked, no recovery path in contract
assertEq(receiver.rate(), oldRate);
assertTrue(endpoint.hasStoredPayload(A, srcAddressBytes));
``` [7](#0-6)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L11-11)
```text
abstract contract CrossChainRateReceiver is ILayerZeroReceiver, Ownable {
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L72-76)
```text
    function updateSrcChainId(uint16 _srcChainId) external onlyOwner {
        srcChainId = _srcChainId;

        emit SrcChainIdUpdated(_srcChainId);
    }
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-100)
```text
    function lzReceive(uint16 _srcChainId, bytes memory _srcAddress, uint64, bytes calldata _payload) external {
        require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");

        address srcAddress;
        assembly {
            srcAddress := mload(add(_srcAddress, 20))
        }

        require(_srcChainId == srcChainId, "Src chainId must be correct");
        require(srcAddress == rateProvider, "Src address must be provider");

        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
    }
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L102-105)
```text
    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/external/layerzero/interfaces/ILayerZeroEndpoint.sol (L74-78)
```text
    // @notice the interface to retry failed message on this Endpoint destination
    // @param _srcChainId - the source chain identifier
    // @param _srcAddress - the source chain contract address
    // @param _payload - the payload to be retried
    function retryPayload(uint16 _srcChainId, bytes calldata _srcAddress, bytes calldata _payload) external;
```

**File:** contracts/external/layerzero/interfaces/ILayerZeroUserApplicationConfig.sol (L21-24)
```text
    // @notice Only when the UA needs to resume the message flow in blocking mode and clear the stored payload
    // @param _srcChainId - the chainId of the source chain
    // @param _srcAddress - the contract address of the source contract at the source chain
    function forceResumeReceive(uint16 _srcChainId, bytes calldata _srcAddress) external;
```
