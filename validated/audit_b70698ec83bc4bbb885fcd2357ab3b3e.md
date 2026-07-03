Audit Report

## Title
Excess ETH Sent to `updateRate()` Is Permanently Locked in `MultiChainRateProvider` - (File: contracts/cross-chain/MultiChainRateProvider.sol)

## Summary
`MultiChainRateProvider.updateRate()` is a `payable` function that sends exactly `estimatedFee` to the LayerZero endpoint per receiver in a loop, but never refunds the difference between `msg.value` and the total fees consumed. The contract inherits only `Ownable` and `ReentrancyGuard`, exposes no `withdraw` function, no `receive` fallback, and no ETH recovery mechanism, making any over-payment permanently irrecoverable.

## Finding Description
In `MultiChainRateProvider.updateRate()` (L108–137), the loop at L119–134 calls `ILayerZeroEndpoint.send{ value: estimatedFee }(...)` for each receiver, consuming only the per-receiver `estimatedFee`. The refund address passed to LayerZero is `payable(msg.sender)` (L128), so LayerZero refunds any per-call excess back to the caller. However, the contract itself never refunds `msg.value - sum(estimatedFees)` after the loop completes. The full contract (L1–182) contains no `receive()`, no `fallback()`, and no `withdraw` function, so any ETH remainder accumulates in the contract with no recovery path.

This contrasts directly with `CrossChainRateProvider.updateRate()` (L85–101), which passes `send{ value: msg.value }(...)` (L96), forwarding the entire `msg.value` to LayerZero so its own refund mechanism handles any excess correctly.

## Impact Explanation
Any ETH sent above the exact sum of per-receiver `estimatedFee` values is permanently frozen inside `MultiChainRateProvider`. Because the contract has no ETH recovery mechanism whatsoever, this constitutes **permanent freezing of funds**, a Critical impact under the allowed scope.

## Likelihood Explanation
`updateRate()` is a public, permissionless function callable by any external account. Fee estimates from `estimateTotalFee()` can shift between the off-chain query and on-chain execution due to gas price changes or oracle updates, so callers routinely add a safety buffer. Every such over-payment permanently loses the buffer. The function is expected to be called repeatedly by any party wishing to push the rsETH rate cross-chain, making this a recurring loss vector.

## Recommendation
After the loop, refund any unspent ETH to `msg.sender`:

```solidity
function updateRate() external payable nonReentrant {
    // ... existing logic ...
    for (...) { ... }

    uint256 remaining = address(this).balance;
    if (remaining > 0) {
        (bool ok,) = payable(msg.sender).call{ value: remaining }("");
        require(ok, "ETH refund failed");
    }
    emit RateUpdated(rate);
}
```

Alternatively, compute `totalFee` before the loop using `estimateTotalFee()` and require `msg.value == totalFee` to enforce exact payment.

## Proof of Concept
1. Call `estimateTotalFee()` off-chain → returns `X` wei.
2. Call `updateRate{ value: X + 1 ether }()` (caller adds a 1 ETH safety buffer).
3. The loop at L119–134 sends exactly `estimatedFee_i` per receiver; total consumed ≈ `X`.
4. After the function returns, `address(MultiChainRateProvider).balance == 1 ether`.
5. Inspect the contract: no `withdraw`, no `receive`, no `fallback` exists anywhere in L1–182.
6. The 1 ETH is permanently locked with no recovery path.