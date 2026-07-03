### Title
Excess Native ETH Sent to `MultiChainRateProvider.updateRate()` Is Permanently Trapped in the Contract - (File: contracts/cross-chain/MultiChainRateProvider.sol)

### Summary
`MultiChainRateProvider.updateRate()` is a permissionless `payable` function that distributes LayerZero fees across multiple destination chains. It consumes exactly `estimatedFee` per receiver from `msg.value`, but never checks that `msg.value` equals the total required fee and never refunds any excess. Any ETH sent beyond the sum of per-chain fees is permanently locked in the contract, which has no withdrawal mechanism.

### Finding Description
`MultiChainRateProvider.updateRate()` iterates over all configured `rateReceivers`, calls `estimateFees()` on the LayerZero endpoint for each, and forwards exactly that amount via `send{ value: estimatedFee }`:

```solidity
for (uint256 i; i < rateReceiversLength;) {
    uint16 dstChainId = uint16(rateReceivers[i]._chainId);
    bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceivers[i]._contract, address(this));

    (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
        .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

    ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
        dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
    );
    ...
}
```

The function has no guard of the form `require(msg.value == totalFee)` or `require(msg.value >= totalFee)` before the loop, and no refund of `msg.value - totalConsumed` after the loop. The contract inherits only `Ownable` and `ReentrancyGuard` and defines no `withdraw` or `receive`-with-sweep function, so any excess ETH is permanently unrecoverable.

By contrast, `CrossChainRateProvider.updateRate()` (the single-chain variant) passes the entire `msg.value` directly to the LZ endpoint with `{ value: msg.value }` and supplies `payable(msg.sender)` as the refund address, so the LZ endpoint itself returns any excess — that contract is not affected. [1](#0-0) [2](#0-1) 

### Impact Explanation
Any ETH sent above the sum of per-chain `estimatedFee` values is permanently frozen inside `MultiChainRateProvider`. The contract exposes `estimateTotalFee()` as a view helper, but on-chain fee estimates can shift between the view call and the actual transaction (e.g., due to gas price changes or LZ config updates). A caller who adds a small buffer to avoid an out-of-gas revert mid-loop will permanently lose that buffer. Because the contract has no sweep or withdraw path, the loss is irreversible.

Impact classification: **Low — contract fails to deliver promised returns (excess ETH is not returned to the caller)**, with a path to **Medium — permanent freezing of unclaimed yield** if the trapped ETH accumulates over many calls. [3](#0-2) 

### Likelihood Explanation
`updateRate()` carries no access control — any external account can call it. Callers who consult `estimateTotalFee()` off-chain and then submit a transaction with a small ETH buffer (a common defensive pattern when fees are volatile) will silently lose the buffer. The function is also callable by keeper bots that may over-provision ETH to guarantee execution. Likelihood is **Low-to-Medium** given the permissionless entry point and the common practice of adding a fee buffer. [4](#0-3) 

### Recommendation
After the loop, compute the total consumed fee and refund any remainder to `msg.sender`:

```solidity
function updateRate() external payable nonReentrant {
    uint256 latestRate = getLatestRate();
    rate = latestRate;
    lastUpdated = block.timestamp;
    bytes memory _payload = abi.encode(latestRate);
    uint256 rateReceiversLength = rateReceivers.length;
    uint256 totalConsumed;

    for (uint256 i; i < rateReceiversLength;) {
        uint16 dstChainId = uint16(rateReceivers[i]._chainId);
        bytes memory remoteAndLocalAddresses =
            abi.encodePacked(rateReceivers[i]._contract, address(this));

        (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
            .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
            dstChainId, remoteAndLocalAddresses, _payload,
            payable(msg.sender), address(0x0), bytes("")
        );
        totalConsumed += estimatedFee;
        unchecked { ++i; }
    }

    // Refund excess ETH
    uint256 excess = msg.value - totalConsumed;
    if (excess > 0) {
        (bool ok,) = payable(msg.sender).call{ value: excess }("");
        require(ok, "Refund failed");
    }

    emit RateUpdated(rate);
}
```

Alternatively, add a pre-loop check `require(msg.value >= estimateTotalFee(), "Insufficient fee")` and refund the difference.

### Proof of Concept
1. Deploy `MultiChainRateProvider` with two configured `rateReceivers`.
2. Call `estimateTotalFee()` — suppose it returns `0.01 ETH`.
3. Call `updateRate{ value: 0.02 ETH }()` (caller adds a 2× buffer to be safe).
4. The loop consumes exactly `0.01 ETH` across the two LZ sends.
5. The remaining `0.01 ETH` stays in the contract's balance.
6. No function exists to recover it; the ETH is permanently frozen. [5](#0-4)

### Citations

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-137)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        uint256 rateReceiversLength = rateReceivers.length;

        for (uint256 i; i < rateReceiversLength;) {
            uint16 dstChainId = uint16(rateReceivers[i]._chainId);

            bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceivers[i]._contract, address(this));

            (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
                .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

            ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
                dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
            );

            unchecked {
                ++i;
            }
        }

        emit RateUpdated(rate);
    }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L152-173)
```text
    /// @notice Estimate the fees of sending an update to all chains/receiver contracts
    /// @return totalEstimatedFee the total estimated fee
    function estimateTotalFee() external view returns (uint256 totalEstimatedFee) {
        uint256 latestRate = getLatestRate();

        bytes memory _payload = abi.encode(latestRate);

        uint256 rateReceiversLength = rateReceivers.length;

        for (uint256 i; i < rateReceiversLength;) {
            uint16 dstChainId = uint16(rateReceivers[i]._chainId);

            (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
                .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

            totalEstimatedFee += estimatedFee;

            unchecked {
                ++i;
            }
        }
    }
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L85-101)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceiver, address(this));

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );

        emit RateUpdated(rate);
    }
```
