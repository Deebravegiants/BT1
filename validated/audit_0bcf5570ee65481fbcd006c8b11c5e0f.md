Audit Report

## Title
Excess ETH Permanently Locked in `MultiChainRateProvider` Due to Missing Recovery Mechanism - (File: contracts/cross-chain/MultiChainRateProvider.sol)

## Summary
`MultiChainRateProvider.updateRate()` is a public `payable` function that sends exactly `estimatedFee` per registered receiver to LayerZero, but provides no mechanism to refund or recover any `msg.value` in excess of the total fees consumed. The contract inherits only `Ownable` and `ReentrancyGuard`, with no `recoverETH()`, no `receive()` sweep, and no admin withdrawal. Any ETH overpayment is permanently frozen in the contract with no recovery path for any role.

## Finding Description
`updateRate()` iterates over all `rateReceivers`, re-estimates the LayerZero fee for each at call time, and forwards exactly `estimatedFee` per receiver:

```solidity
(uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
    .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
```

The function accepts arbitrary `msg.value`. After the loop, `msg.value - sum(estimatedFee_i)` remains in `address(this).balance`. The contract has no function to retrieve it — confirmed by the full contract source and grep across all cross-chain contracts showing zero matches for `recoverETH`, `receive()`, or any withdrawal function.

The contract inherits only `Ownable` and `ReentrancyGuard`, not `Recoverable`. Both concrete deployments — `RSETHMultiChainRateProvider` and `AGETHMultiChainRateProvider` — inherit this same abstract contract and add no recovery logic of their own.

By contrast, `LineaMessenger` — a fee-paying bridge helper in the same codebase — explicitly guards against this with `if (msg.value != value) revert MismatchedMsgValue()` and a comment reading *"avoid trapping ETH in this contract"*, demonstrating developer awareness of the pattern. `LineaMessenger` also inherits `Recoverable` for a belt-and-suspenders defense.

## Impact Explanation
**Critical — Permanent freezing of funds.** Any ETH sent to `updateRate()` beyond the exact sum of on-chain LayerZero fee estimates is irrecoverably locked. No owner, admin, or privileged role can retrieve it. The contracts are rate-propagation contracts expected to be called repeatedly over their operational lifetime, so residual balances accumulate monotonically. If the contracts are deprecated or replaced, all accumulated ETH is permanently lost.

## Likelihood Explanation
`updateRate()` is a public `payable` function callable by any address. Callers must estimate the total fee off-chain before calling and will routinely send a small buffer above the estimate to avoid reverts due to fee fluctuation between estimation and execution. Every such call that overshoots leaves a residual. The `estimateTotalFee()` view function exists but the actual fees used inside `updateRate()` are re-estimated at call time, so a discrepancy is structurally unavoidable. No special attacker capability is required — normal operational use is sufficient.

## Recommendation
Add an owner-restricted ETH recovery function to `MultiChainRateProvider`:

```solidity
function recoverETH(address recipient, uint256 amount) external onlyOwner {
    require(recipient != address(0));
    require(amount > 0 && address(this).balance >= amount);
    (bool success,) = payable(recipient).call{ value: amount }("");
    require(success, "Transfer failed");
}
```

Alternatively, have `MultiChainRateProvider` inherit `Recoverable` (as `LineaMessenger` does) to gain both `recoverETH()` and `recoverTokens()`. A stricter option is to enforce exact payment by reverting if `msg.value` exceeds the total estimated fee, analogous to `LineaMessenger`'s `MismatchedMsgValue` guard.

## Proof of Concept
1. Deploy `RSETHMultiChainRateProvider` with two `rateReceivers` on different chains.
2. Call `estimateTotalFee()` — returns 0.02 ETH (0.01 ETH per receiver).
3. Call `updateRate{ value: 0.025 ETH }()`.
4. The loop sends 0.01 ETH to LayerZero for receiver 0, then 0.01 ETH for receiver 1.
5. `address(this).balance` is now 0.005 ETH.
6. Attempt to call any recovery function — none exists. The 0.005 ETH is permanently locked.
7. Repeat over the contract's lifetime; balance grows with no bound and no recovery path.

**Foundry test sketch:**
```solidity
function test_excessEthLocked() public {
    // mock LayerZero endpoint returning estimatedFee = 0.01 ether per receiver
    vm.deal(caller, 1 ether);
    vm.prank(caller);
    provider.updateRate{ value: 0.025 ether }();
    assertEq(address(provider).balance, 0.005 ether);
    // no recoverETH exists — any call to retrieve it reverts
}
```