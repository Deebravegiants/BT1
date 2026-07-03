Audit Report

## Title
`MultiChainRateProvider.updateRate()` Reverts Mid-Loop When `msg.value` Is Insufficient to Cover Cumulative LayerZero Fees - (File: contracts/cross-chain/MultiChainRateProvider.sol)

## Summary
`updateRate()` estimates and immediately forwards LayerZero fees per receiver inside a single loop with no pre-flight check that `msg.value` covers the cumulative total. If the supplied ETH is exhausted before all receivers are served, the EVM reverts the entire transaction, leaving all L2 rate receivers with a stale rsETH/ETH exchange rate. The `estimateTotalFee()` helper exists but is never enforced on-chain.

## Finding Description
In `MultiChainRateProvider.updateRate()` (lines 119–134), each loop iteration calls `ILayerZeroEndpoint.estimateFees(...)` and immediately forwards the result via `send{ value: estimatedFee }(...)`. The contract's ETH balance decreases by `estimatedFee` on every iteration. There is no guard of the form `require(msg.value >= totalFee)` before the loop begins. [1](#0-0) 

Because LayerZero fees are dynamic, the sum of per-receiver fees at execution time can exceed the value estimated off-chain. When `address(this).balance < estimatedFee` on any iteration, the `send` call reverts with an out-of-funds error, rolling back the entire transaction. The `estimateTotalFee()` view function (lines 154–173) computes the correct total but is never called inside `updateRate()` to enforce a minimum. [2](#0-1) 

## Impact Explanation
When the transaction reverts, `rate` and `lastUpdated` are not written, and no LayerZero message is dispatched to any receiver. All downstream L2 pool contracts that consume this rate continue operating on a stale value. This matches the allowed impact: **Low — Contract fails to deliver promised returns, but doesn't lose value.**

## Likelihood Explanation
`updateRate()` is `external payable` with no access control. [3](#0-2) 

Any caller — including keeper bots — can invoke it. LayerZero fees fluctuate with network congestion; the probability of a mismatch grows with the number of registered receivers. No special privileges or victim mistakes are required.

## Recommendation
Perform a two-pass approach: first accumulate all estimated fees into a `fees[]` array and validate `msg.value >= totalFee`, then execute all `send` calls using the pre-computed values. This eliminates both the mid-loop revert risk and the TOCTOU window between estimation and execution.

## Proof of Concept
1. Deploy `MultiChainRateProvider` with two receivers on different chains.
2. Call `estimateTotalFee()` off-chain → returns `X` wei.
3. Call `updateRate{ value: X - 1 }()` (or call with `X` while fees rise by 1 wei before the block is mined).
4. Iteration 0: `send{ value: fee_0 }` succeeds, consuming `fee_0` from the contract balance.
5. Iteration 1: `send{ value: fee_1 }` is attempted; `address(this).balance < fee_1` → EVM reverts.
6. Entire transaction rolls back; `rate`, `lastUpdated`, and all receiver states remain unchanged.

### Citations

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-108)
```text
    function updateRate() external payable nonReentrant {
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L119-134)
```text
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
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L154-173)
```text
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
