Audit Report

## Title
Bare Loop in `updateRate()` Allows Single Failing Destination to Block All L2 Rate Updates - (File: `contracts/cross-chain/MultiChainRateProvider.sol`)

## Summary
`MultiChainRateProvider.updateRate()` iterates over all registered `rateReceivers` and calls `ILayerZeroEndpoint.send` for each without any per-entry error isolation. If the LayerZero `send` call reverts for any single destination — due to a temporarily unavailable path, a broken receiver contract, or fee drift — the entire transaction reverts atomically. No chain receives the updated rate, causing all L2 pools to operate on a stale rsETH/ETH exchange rate. Because rsETH is monotonically appreciating, a stale (lower) rate allows L2 users to acquire rsETH at a discount, extracting yield that belongs to existing rsETH holders.

## Finding Description
`updateRate()` is `external payable nonReentrant` with no access control. Inside the function, a `for` loop iterates over `rateReceivers`, computes `estimatedFee` via `ILayerZeroEndpoint.estimateFees`, and immediately calls `ILayerZeroEndpoint.send{ value: estimatedFee }`:

```solidity
// contracts/cross-chain/MultiChainRateProvider.sol L119-134
for (uint256 i; i < rateReceiversLength;) {
    uint16 dstChainId = uint16(rateReceivers[i]._chainId);
    bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceivers[i]._contract, address(this));

    (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
        .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

    ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
        dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
    );

    unchecked { ++i; }
}
```

There is no `try/catch` around the `send` call. A revert at iteration `i` unwinds the entire call stack, including all successful sends at iterations `0..i-1`. The `removeRateReceiver` function exists but is `onlyOwner`, meaning a broken receiver cannot be bypassed by any unprivileged caller. Until the owner intervenes, every `updateRate` call fails for all chains.

## Impact Explanation
L2 pools (e.g., `RSETHPoolV3`) consume the rate pushed by `MultiChainRateProvider` to price ETH→rsETH swaps. When rate propagation is blocked:

- All registered L2 pools operate on the last committed stale rate.
- rsETH accrues yield on L1 continuously; the stale L2 rate diverges downward over time.
- Any user can swap ETH for rsETH on L2 at the stale (lower) rate, receiving more rsETH than the current fair value entitles them to.
- The excess rsETH comes at the expense of existing rsETH holders whose accrued yield is diluted.

This constitutes **Theft of unclaimed yield** (High), with a secondary **Permanent freezing of unclaimed yield** (Medium) for the duration of the outage.

## Likelihood Explanation
The function is callable by any external account. Concrete, non-theoretical triggers include:

1. **LayerZero path temporarily unavailable**: Any registered destination chain's LZ path going offline causes every `updateRate` call to revert until the path recovers or the owner removes the receiver.
2. **Broken/paused receiver contract**: If a receiver on any registered chain is upgraded, paused, or misconfigured, the endpoint reverts on delivery attempt.
3. **Fee drift**: Although `estimateFees` and `send` occur in the same transaction, the LZ endpoint can enforce a minimum fee that differs from the estimate under certain conditions.

With multiple L2 chains registered simultaneously, the probability that at least one chain experiences a transient issue at any given time is non-negligible. The outage persists until the owner calls `removeRateReceiver`, which may not happen promptly.

## Recommendation
Wrap each `ILayerZeroEndpoint.send` call in a `try/catch` block and emit a failure event, so a single failing destination does not prevent rate propagation to all other chains:

```solidity
try ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
) {
    // success
} catch (bytes memory reason) {
    emit RateUpdateFailed(dstChainId, rateReceivers[i]._contract, reason);
}
```

Additionally, consider pre-validating that `msg.value` covers the sum of all estimated fees (via `estimateTotalFee`) before entering the loop, and refunding any excess ETH to the caller.

## Proof of Concept

1. Deploy a concrete subclass of `MultiChainRateProvider` with two `rateReceivers`: chain A (healthy LZ path) and chain B (receiver contract broken or LZ path paused).
2. Call `updateRate()` with sufficient ETH to cover both fees.
3. The loop reaches chain B; `ILayerZeroEndpoint.send` reverts.
4. The entire transaction reverts — chain A also receives no rate update.
5. Repeat: every subsequent `updateRate` call reverts until the owner calls `removeRateReceiver` for chain B.
6. During the outage window, rsETH accrues yield on L1. An arbitrageur calls the L2 pool's swap function, receiving rsETH at the stale (lower) rate, extracting yield from existing rsETH holders.

Foundry fork test outline:
- Fork mainnet + target L2.
- Mock `ILayerZeroEndpoint.send` to revert for chain B's `dstChainId`.
- Assert `updateRate()` reverts.
- Assert chain A's receiver still holds the pre-outage stale rate.
- Compute yield delta over N blocks and assert L2 swap returns more rsETH than the current fair-value rate would allow. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L81-102)
```text
    function removeRateReceiver(uint256 _index) external onlyOwner {
        // Store the rate receiver in a memory var
        RateReceiver memory _rateReceiverToBeRemoved = rateReceivers[_index];

        // Get the current length of all the rate receivers
        uint256 rateReceiversLength = rateReceivers.length;

        // Get the last index of the all the rate receivers
        uint256 lastIndex = rateReceiversLength - 1;

        if (lastIndex != _index) {
            // Get the last rate receiver
            RateReceiver memory lastValue = rateReceivers[lastIndex];

            // Replace the index value with the last index value
            rateReceivers[_index] = lastValue;
        }

        rateReceivers.pop();

        emit RateReceiverRemoved(_rateReceiverToBeRemoved._chainId, _rateReceiverToBeRemoved._contract);
    }
```

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
