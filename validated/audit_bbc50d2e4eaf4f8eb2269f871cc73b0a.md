Audit Report

## Title
Arithmetic Underflow in `bridgeKernelToBSC` Temporarily Blocks Bridging When `counter == 0` — (`contracts/KERNEL/KernelVaultETH.sol`)

## Summary
`bridgeKernelToBSC` unconditionally executes `lastBridgedDepositId = counter - 1` at line 262 before performing any bridge operation. When `counter == 0` — the default state at deployment, before any `depositKernel` call — Solidity 0.8.27 checked arithmetic causes an underflow panic revert, making the function uncallable. Any KERNEL balance present in the vault at that point (including tokens sent via direct ERC20 transfer) cannot be bridged until `counter` is incremented to at least 1.

## Finding Description
`counter` is a `uint256` storage variable initialized to zero. It is incremented exclusively inside `_depositKernel` at line 394 (`++counter`). `bridgeKernelToBSC` performs no guard on `counter` before computing `counter - 1` at line 262. Under Solidity 0.8.27 checked arithmetic, `0 - 1` triggers an `Panic(0x11)` revert. Because KERNEL is a plain ERC20 with no transfer hooks, any address holding KERNEL tokens can call `kernel.transfer(address(vault), amount)` directly, placing tokens in the vault without incrementing `counter`. There is no rescue or sweep function in `KernelVaultETH`, making `bridgeKernelToBSC` the sole egress path for KERNEL. The freeze persists until the operator (or any user) calls `depositKernel(minDeposit)`, which sets `counter = 1`, after which `counter - 1 = 0` is valid and `bridgeKernelToBSC` succeeds, bridging the full vault balance including any directly-transferred tokens.

## Impact Explanation
**Medium — Temporary freezing of funds.** KERNEL tokens present in the vault cannot be bridged while `counter == 0`. The condition is externally triggerable by any KERNEL token holder via a direct ERC20 transfer to the vault address. The operator can self-remediate by calling `depositKernel(minDeposit)`, making the freeze temporary rather than permanent. The impact is a real, externally-triggerable DoS on the bridge function during the deployment window.

## Likelihood Explanation
Low-to-medium. The vulnerable window exists from deployment until the first successful `depositKernel` call. A direct ERC20 transfer to the vault is trivially executable by any KERNEL holder with no special privileges. The operator can self-remediate, but the bug is silently present and could delay bridging operations or cause confusion in production.

## Recommendation
Add a guard in `bridgeKernelToBSC` before computing `lastBridgedDepositId`:

```solidity
if (counter == 0) revert NoDepositsYet();
lastBridgedDepositId = counter - 1;
```

Alternatively, initialize `lastBridgedDepositId` to `type(uint256).max` as a sentinel value and handle the zero-counter case explicitly, or restructure bookkeeping so `lastBridgedDepositId` is only written when `counter > 0`.

## Proof of Concept
```solidity
// 1. Deploy KernelVaultETH (counter == 0, lastBridgedDepositId == 0)

// 2. Any KERNEL holder directly transfers tokens to the vault
kernel.transfer(address(vault), 1e18);
// counter remains 0

// 3. Operator attempts to bridge — reverts with Panic(0x11) arithmetic underflow
vault.bridgeKernelToBSC{value: fee}(1e18, 0.99e18, fee, refundAddress);
// ↑ panics at line 262: lastBridgedDepositId = counter - 1  (0 - 1 underflows)

// 4. Operator self-remediates
kernel.approve(address(vault), minDeposit);
vault.depositKernel(minDeposit); // counter becomes 1

// 5. Bridge now succeeds, bridging full vault balance
vault.bridgeKernelToBSC{value: fee}(kernel.balanceOf(address(vault)), ...);
```