Audit Report

## Title
Excess ETH Permanently Locked in `MultiChainRateProvider` When `updateRate()` Overpays LayerZero Fees - (File: contracts/cross-chain/MultiChainRateProvider.sol)

## Summary
`MultiChainRateProvider.updateRate()` is a public payable function that forwards only the on-chain `estimatedFee` per receiver to LayerZero, retaining any excess `msg.value` in the contract. The contract has no `receive()` fallback, no `withdraw()`, and no ETH recovery function, making any retained ETH permanently unrecoverable.

## Finding Description
In `MultiChainRateProvider.updateRate()` (L108–137), the function iterates over all `rateReceivers`, calls `ILayerZeroEndpoint.estimateFees()` on-chain for each, and forwards exactly that `estimatedFee` to `ILayerZeroEndpoint.send()`:

```solidity
(uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
    .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
```

The `payable(msg.sender)` argument is LayerZero's cross-chain refund address (for excess gas on the destination chain), not a mechanism to refund excess `msg.value` held by this contract. After the loop completes, any `msg.value` exceeding the sum of all per-receiver `estimatedFee` values remains in `MultiChainRateProvider` with no code path to recover it.

The contract defines only four state-mutating functions: `updateLayerZeroEndpoint`, `addRateReceiver`, `removeRateReceiver` (all `onlyOwner`), and `updateRate` (public). None drain the contract's ETH balance. There is no `receive()` or `fallback()` function, and no `withdraw()` or sweep function.

This contrasts directly with `CrossChainRateProvider.updateRate()` (L96–98), which passes `msg.value` in full to `send()`, allowing LayerZero to refund any excess natively:

```solidity
ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
```

`MultiChainRateProvider` does not replicate this pattern.

## Impact Explanation
Any ETH sent in excess of the sum of per-receiver `estimatedFee` values at execution time is permanently locked in the contract. There is no owner-callable or user-callable recovery path. This constitutes **permanent freezing of funds** (Critical).

## Likelihood Explanation
`updateRate()` is a public function callable by any external account. LayerZero fees are gas-price-sensitive and fluctuate block-to-block. Callers are directed by the contract's own NatSpec to pre-estimate fees via `estimateTotalFee()` and routinely add a safety buffer to avoid reverts — a standard cross-chain practice. Any such buffer, or any drop in destination-chain gas prices between off-chain estimation and on-chain inclusion, causes excess ETH to be locked. This is a normal operating condition, not an edge case.

## Recommendation
After the loop in `updateRate()`, refund any remaining contract balance to `msg.sender`:

```solidity
uint256 remaining = address(this).balance;
if (remaining > 0) {
    (bool success,) = payable(msg.sender).call{ value: remaining }("");
    require(success, "Refund failed");
}
```

Alternatively, mirror `CrossChainRateProvider` by passing `msg.value` split proportionally (or entirely) to each `send()` call and relying on LayerZero's built-in refund mechanism.

## Proof of Concept
1. Deploy `MultiChainRateProvider` with 3 `rateReceivers`.
2. Call `estimateTotalFee()` off-chain; it returns `0.009 ETH`.
3. Call `updateRate{ value: 0.011 ETH }()` (standard 20% buffer).
4. At execution time, destination-chain gas prices have dropped; `estimateFees()` returns `0.002 ETH` per receiver (total `0.006 ETH`).
5. The loop sends `0.006 ETH` total to LayerZero across 3 `send()` calls.
6. `0.005 ETH` (`0.011 - 0.006`) remains in `MultiChainRateProvider`.
7. Confirm: no function in the contract can drain this balance. The ETH is permanently locked.

Foundry fork test: deploy against a mainnet/testnet fork with a live LayerZero endpoint, call `updateRate` with `msg.value` exceeding `estimateTotalFee()`, then assert `address(multiChainRateProvider).balance > 0` after the call and that no subsequent call reduces it to zero.