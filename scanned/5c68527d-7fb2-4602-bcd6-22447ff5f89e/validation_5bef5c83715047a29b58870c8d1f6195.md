### Title
Missing Zero-Address Validation in `CrossChainRateReceiver` Setter Functions Permanently Breaks L2 Rate Oracle — (File: `contracts/cross-chain/CrossChainRateReceiver.sol`)

### Summary
`CrossChainRateReceiver.updateLayerZeroEndpoint` and `updateRateReceiver.updateRateProvider` accept address parameters with no zero-address guard. If either is accidentally set to `address(0)`, the `lzReceive` entry point is permanently bricked, freezing the exchange rate used by every L2 liquidity pool that depends on this oracle.

### Finding Description
`CrossChainRateReceiver` exposes two owner-callable setters that write critical address state without validation:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol
function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
    layerZeroEndpoint = _layerZeroEndpoint;          // no zero-address check
    emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
}

function updateRateProvider(address _rateProvider) external onlyOwner {
    rateProvider = _rateProvider;                    // no zero-address check
    emit RateProviderUpdated(_rateProvider);
}
``` [1](#0-0) 

The only path through which the rate can ever be updated is `lzReceive`, which enforces both values as hard guards:

```solidity
function lzReceive(...) external {
    require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");
    ...
    require(srcAddress == rateProvider, "Src address must be provider");
    ...
    rate = _rate;
}
``` [2](#0-1) 

- If `layerZeroEndpoint` is set to `address(0)`, `msg.sender` can never equal `address(0)`, so `lzReceive` always reverts.
- If `rateProvider` is set to `address(0)`, the decoded `srcAddress` from a real LayerZero message can never be `address(0)`, so `lzReceive` always reverts.

Either mistake permanently freezes `rate` at its last stored value with no on-chain recovery path other than a corrective admin call.

The same pattern exists in `CrossChainRateProvider`:

```solidity
function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
    layerZeroEndpoint = _layerZeroEndpoint;   // no zero-address check
    ...
}
function updateRateReceiver(address _rateReceiver) external onlyOwner {
    rateReceiver = _rateReceiver;             // no zero-address check
    ...
}
``` [3](#0-2) 

If `layerZeroEndpoint` is zeroed here, `updateRate()` calls `ILayerZeroEndpoint(address(0)).send(...)`, which reverts, blocking all outbound rate pushes. [4](#0-3) 

And in `MultiChainRateProvider`, `updateLayerZeroEndpoint` and `addRateReceiver` carry the same omission: [5](#0-4) 

### Impact Explanation
Every L2 pool (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolNoWrapper`, etc.) calls `IOracle(rsETHOracle).getRate()` to price deposits:

```solidity
uint256 rsETHToETHrate = getRate();          // reads from CrossChainRateReceiver
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [6](#0-5) 

A frozen rate means the oracle returns a stale (lower-than-actual) rsETH/ETH price as staking rewards accumulate. New depositors receive more `wrsETH` than they are entitled to, diluting existing holders' accrued yield. The protocol cannot deliver the promised exchange rate to existing `wrsETH` holders. Impact: **Low — Contract fails to deliver promised returns**.

### Likelihood Explanation
The setters are `onlyOwner`. Accidental misconfiguration (e.g., passing `address(0)` during a routine update or a scripting error) is a realistic operational risk, especially given that the analogous pattern was already exploited in the referenced audit. No malicious actor is required.

### Recommendation
Add `UtilLib.checkNonZeroAddress` guards to all four setters:

```solidity
function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
    UtilLib.checkNonZeroAddress(_layerZeroEndpoint);
    layerZeroEndpoint = _layerZeroEndpoint;
    emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
}

function updateRateProvider(address _rateProvider) external onlyOwner {
    UtilLib.checkNonZeroAddress(_rateProvider);
    rateProvider = _rateProvider;
    emit RateProviderUpdated(_rateProvider);
}
```

Apply the same fix to `CrossChainRateProvider.updateRateReceiver` and `MultiChainRateProvider.addRateReceiver`.

### Proof of Concept
1. Owner calls `CrossChainRateReceiver.updateLayerZeroEndpoint(address(0))` (e.g., scripting error passes wrong argument).
2. `layerZeroEndpoint` is now `address(0)`.
3. LayerZero delivers a rate update; `lzReceive` is called with `msg.sender = <real LZ endpoint>`.
4. `require(msg.sender == layerZeroEndpoint)` → `require(<real endpoint> == address(0))` → **reverts**.
5. `rate` is permanently frozen at its last value.
6. All L2 pools calling `getRate()` on this receiver return the stale rate.
7. As rsETH accrues staking yield, new depositors receive inflated `wrsETH` amounts, diluting existing holders.

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L54-67)
```text
    function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
        layerZeroEndpoint = _layerZeroEndpoint;

        emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
    }

    /// @notice Updates the RateProvider address
    /// @dev Can only be called by owner
    /// @param _rateProvider the new rate provider address
    function updateRateProvider(address _rateProvider) external onlyOwner {
        rateProvider = _rateProvider;

        emit RateProviderUpdated(_rateProvider);
    }
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-99)
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
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L57-70)
```text
    function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
        layerZeroEndpoint = _layerZeroEndpoint;

        emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
    }

    /// @notice Updates the RateReceiver address
    /// @dev Can only be called by owner
    /// @param _rateReceiver the new rate receiver address
    function updateRateReceiver(address _rateReceiver) external onlyOwner {
        rateReceiver = _rateReceiver;

        emit RateReceiverUpdated(_rateReceiver);
    }
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L96-98)
```text
        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L62-76)
```text
    function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
        layerZeroEndpoint = _layerZeroEndpoint;

        emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
    }

    /// @notice Adds a rate receiver
    /// @dev Can only be called by owner
    /// @param _chainId rate receiver chainId
    /// @param _contract rate receiver address
    function addRateReceiver(uint16 _chainId, address _contract) external onlyOwner {
        rateReceivers.push(RateReceiver({ _chainId: _chainId, _contract: _contract }));

        emit RateReceiverAdded(_chainId, _contract);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L304-307)
```text
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
