Audit Report

## Title
Excess ETH Permanently Frozen in `updateRate()` Due to Missing Post-Loop Refund — (File: contracts/cross-chain/MultiChainRateProvider.sol)

## Summary
`MultiChainRateProvider.updateRate()` is an unrestricted `payable` function that forwards exactly `estimatedFee` per destination chain to LayerZero, consuming only the sum of per-chain estimates from `msg.value`. Any ETH sent beyond that sum has no refund path and no recovery mechanism in the contract, permanently freezing the excess. The concrete implementations `RSETHMultiChainRateProvider` and `AGETHMultiChainRateProvider` add no recovery function either.

## Finding Description
`updateRate()` (L108–137) iterates over all `rateReceivers`, re-estimates the fee on-chain for each destination, and forwards exactly that amount:

```solidity
(uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
    .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
```

The `payable(msg.sender)` refund address passed to LayerZero's `send` only covers any excess *within* that individual `send` call (i.e., if `estimatedFee` slightly exceeds the actual fee consumed by LayerZero). It does **not** refund `msg.value − Σ(estimatedFees)` back to the caller. After the loop completes, no code touches `address(this).balance`.

The contract inherits only `Ownable` and `ReentrancyGuard` — neither provides ETH recovery. The two concrete implementations (`RSETHMultiChainRateProvider`, `AGETHMultiChainRateProvider`) are non-upgradeable and add no sweep or rescue function.

Contrast with `CrossChainRateProvider.updateRate()` (L96), which passes `msg.value` directly to `send`, delegating all refund handling to LayerZero:
```solidity
ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(...)
```
`MultiChainRateProvider` deliberately departs from this pattern but omits the compensating refund.

Critically, callers **must** overpay to avoid reverts: `estimateTotalFee()` is a view function called off-chain, but the actual fees are re-estimated on-chain inside the loop. If fees rise between the off-chain estimate and on-chain execution, the transaction reverts for insufficient ETH. This forces callers to include a safety buffer — which is then permanently frozen.

## Impact Explanation
Any ETH sent in excess of `Σ(estimatedFees)` is permanently locked in `MultiChainRateProvider`. The contract is not upgradeable and has no ETH recovery path. This constitutes **permanent freezing of funds**, matching the Critical impact class. The frozen amount equals the caller's safety buffer, which is a necessary and expected component of any cross-chain gas payment.

## Likelihood Explanation
`updateRate()` has no access control — any external account can call it. Because `estimateTotalFee()` is a view function evaluated off-chain while fees are re-estimated on-chain in the loop, callers must add a buffer to avoid reverts from fee increases. This makes overpayment not merely common but structurally required for reliable operation. Every successful call with a non-zero buffer permanently freezes ETH. Likelihood: **Low** (requires overpayment), but the condition is a standard and necessary operational pattern.

## Recommendation
After the loop, refund any remaining contract balance to the caller:

```solidity
function updateRate() external payable nonReentrant {
    // ... existing loop ...
    uint256 remaining = address(this).balance;
    if (remaining > 0) {
        (bool success,) = payable(msg.sender).call{value: remaining}("");
        require(success, "Refund failed");
    }
}
```

Alternatively, compute `estimateTotalFee()` on-chain at the start of `updateRate()`, require `msg.value >= totalFee`, and refund `msg.value − totalFee` after the loop.

## Proof of Concept
1. Deploy `RSETHMultiChainRateProvider` with two `rateReceivers` on different chains.
2. Call `estimateTotalFee()` off-chain — suppose it returns `0.01 ETH`.
3. Call `updateRate{value: 0.02 ether}()` (2× buffer, necessary to avoid reverts from fee fluctuation).
4. The loop re-estimates fees on-chain: `estimatedFee_1 ≈ 0.005 ETH`, `estimatedFee_2 ≈ 0.005 ETH`; LayerZero consumes `≈ 0.01 ETH` total.
5. `address(this).balance == 0.01 ETH` after the loop.
6. No function in `MultiChainRateProvider`, `RSETHMultiChainRateProvider`, or `AGETHMultiChainRateProvider` can recover this ETH — it is permanently frozen.