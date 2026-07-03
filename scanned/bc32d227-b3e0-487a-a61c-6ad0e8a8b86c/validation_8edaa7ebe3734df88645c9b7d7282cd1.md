### Title
Excess ETH Sent to `MultiChainRateProvider.updateRate()` Is Permanently Stuck — No Withdrawal Mechanism Exists - (File: contracts/cross-chain/MultiChainRateProvider.sol)

### Summary
`MultiChainRateProvider.updateRate()` is `payable` and iterates over all registered `rateReceivers`, forwarding exactly `estimatedFee` to the LayerZero endpoint for each one. Any ETH sent by the caller beyond the sum of those estimated fees has no path out of the contract: there is no `receive()` fallback, no `withdraw` function, and no refund logic. The excess is permanently locked.

### Finding Description
`updateRate()` is declared `payable` with the documented intent that callers supply enough ETH to cover LayerZero messaging fees across all destination chains. Inside the loop, each send uses the on-chain `estimatedFee` value — not a proportional slice of `msg.value`:

```solidity
(uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
    .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
```

The LayerZero endpoint receives exactly `estimatedFee` per call, so it has nothing to refund. Any `msg.value` in excess of `∑estimatedFee` across all receivers remains in `MultiChainRateProvider` indefinitely. The contract defines no `receive()`, no `fallback()`, and no admin-accessible withdrawal function, so that ETH is irrecoverable.

### Impact Explanation
Any ETH sent above the exact sum of per-receiver estimated fees is permanently frozen in the contract. Because fee estimates can drift between the off-chain quote and the on-chain execution (e.g., due to gas price changes or payload size differences), callers routinely over-provision ETH as a safety buffer. Every such over-provision results in a permanent, unrecoverable loss of the caller's ETH. This constitutes **permanent freezing of funds**.

### Likelihood Explanation
`updateRate()` has no access control — any address may call it. Callers are explicitly directed to estimate fees off-chain before calling, but fee estimates are inherently approximate. Any caller who sends even 1 wei more than the exact sum of `estimatedFee` values loses that excess permanently. The more `rateReceivers` are registered, the larger the cumulative estimation error and the more likely a meaningful amount of ETH is stranded.

### Recommendation
Add a refund of any unspent ETH to `msg.sender` at the end of `updateRate()`:

```solidity
uint256 remaining = address(this).balance;
if (remaining > 0) {
    (bool ok,) = payable(msg.sender).call{value: remaining}("");
    require(ok, "refund failed");
}
```

Alternatively, add an owner-only `rescueETH()` function, or enforce that `msg.value` equals the pre-computed total fee exactly (reverting otherwise).

### Proof of Concept
1. Deploy a concrete implementation of `MultiChainRateProvider` with two `rateReceivers`.
2. Call `estimateTotalFee()` off-chain → returns, say, `1 ether`.
3. Call `updateRate{ value: 1.01 ether }()`.
4. The loop sends exactly `estimatedFee` (≈ 0.5 ether each) to the LayerZero endpoint for each receiver.
5. The remaining `0.01 ether` (or whatever the over-provision is) stays in the contract.
6. Confirm `address(multiChainRateProvider).balance > 0` after the call.
7. Attempt any withdrawal — no function exists; the ETH is permanently stuck. [1](#0-0) [2](#0-1)

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
