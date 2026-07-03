### Title
Unlimited OFT Adapter Approval with No `amountSentLD` Validation Allows Excess KERNEL Token Drain from Depositor Funds — (File: `contracts/KERNEL/KernelVaultETH.sol`)

---

### Summary

`KernelVaultETH` grants `type(uint256).max` approval to the KERNEL OFT adapter at initialization and never validates `amountSentLD` from the `OFTReceipt` returned by `send()`. In a non-default OFT where the debited amount at origin can exceed the requested `amountLD`, the adapter is free to drain more KERNEL tokens than the operator intended to bridge, consuming tokens belonging to other depositors who have not yet been bridged.

---

### Finding Description

**Root cause 1 — Unlimited approval set at initialization:**

In `KernelVaultETH.initialize()`, the contract permanently grants the OFT adapter an unlimited allowance over every KERNEL token it will ever hold:

```solidity
// contracts/KERNEL/KernelVaultETH.sol L183-186
// Approve the Kernel OFT adapter to spend an unlimited amount of KERNEL tokens on behalf of this contract
// for bridging purposes in order to avoid the need to approve the contract every time a bridging transaction
// is initiated
kernel.forceApprove(address(kernelOftAdapter), type(uint256).max);
``` [1](#0-0) 

This allowance is never revoked or reduced. Every KERNEL token deposited by every user is permanently spendable by the OFT adapter without restriction.

**Root cause 2 — Return value of `send()` is completely discarded:**

In `bridgeKernelToBSC()`, the `OFTReceipt` (which contains both `amountSentLD` and `amountReceivedLD`) is silently dropped:

```solidity
// contracts/KERNEL/KernelVaultETH.sol L264
kernelOftAdapter.send{ value: nativeFee }(sendParam, fee, refundAddress);
``` [2](#0-1) 

Neither field is inspected. The contract has no way to detect that the adapter debited more than `amount`.

**LayerZero's own documentation** (mirrored in the repo's `OFTReceipt` struct comment) explicitly states that `amountSentLD` is the amount *actually* debited and can differ from `amountReceivedLD`:

```solidity
// contracts/interfaces/IKERNEL_OFTAdapter.sol L37-40
struct OFTReceipt {
    uint256 amountSentLD; // Amount of tokens ACTUALLY debited from the sender in local decimals
    uint256 amountReceivedLD; // Amount of tokens to be received on the remote side
}
``` [3](#0-2) 

In a non-default OFT adapter (e.g., one that charges an origin-side fee on top of `amountLD`), `amountSentLD` can exceed `amountLD`. Because the vault holds `type(uint256).max` approval, the adapter can debit the full vault balance rather than just `amount`.

**Contrast with `L1Vault.sol`:** The rsETH bridge uses `safeIncreaseAllowance(address(oftAdapter), amount)` — a per-call, bounded approval — which caps what the adapter can take to exactly `amount`. `KernelVaultETH` uses `type(uint256).max` from day one, making the attack surface materially larger. [4](#0-3) 

---

### Impact Explanation

**Critical — Direct theft of user funds.**

Users deposit KERNEL tokens via the public `depositKernel()` entry point:

```solidity
// contracts/KERNEL/KernelVaultETH.sol L193-195
function depositKernel(uint256 amount) external nonReentrant whenNotPaused {
    _depositKernel(msg.sender, amount);
}
``` [5](#0-4) 

These tokens accumulate in the vault across many depositors. When the operator calls `bridgeKernelToBSC()` with `amount` equal to a subset of the vault balance, a non-default OFT adapter with `type(uint256).max` approval can debit the entire vault balance. The excess over `amount` is taken from tokens belonging to depositors whose funds have not yet been bridged, with no on-chain check to detect or revert the over-debit.

---

### Likelihood Explanation

**Low-to-Medium.** The KERNEL OFT adapter must implement non-default `_debit` logic where `amountSentLD > amountLD` (e.g., an origin-side fee). This is explicitly documented as valid LayerZero behavior. The unlimited approval means no code change is needed on the LRT-rsETH side for the drain to occur — only the adapter's internal accounting needs to differ from the default 1:1 model. If the KERNEL token or its OFT adapter is ever upgraded to include such a fee, all accumulated depositor funds become drainable in a single `bridgeKernelToBSC()` call.

---

### Recommendation

1. **Validate `amountSentLD` after every `send()` call.** Capture the `OFTReceipt` and assert `oftReceipt.amountSentLD == amount`:

```solidity
(, OFTReceipt memory receipt) = kernelOftAdapter.send{ value: nativeFee }(sendParam, fee, refundAddress);
if (receipt.amountSentLD != amount) revert UnexpectedAmountSent();
```

2. **Replace the unlimited approval with a per-call bounded approval.** Instead of `forceApprove(type(uint256).max)` at initialization, approve exactly `amount` before each `send()` call and reset to zero afterward. This caps the maximum the adapter can ever debit to the intended transfer amount, regardless of adapter behavior.

---

### Proof of Concept

1. Alice and Bob each call `depositKernel(1000e18)`. The vault now holds 2000 KERNEL tokens. The OFT adapter has `type(uint256).max` allowance.
2. The operator calls `bridgeKernelToBSC(amount=1000e18, minAmount=900e18, ...)`.
3. The KERNEL OFT adapter's `_debit` implementation charges a 5% origin-side fee, so it debits `1050e18` from the vault (the 1000 requested plus 50 fee tokens).
4. `kernelOftAdapter.send()` returns `OFTReceipt { amountSentLD: 1050e18, amountReceivedLD: 950e18 }`, but the return value is discarded.
5. The vault's KERNEL balance drops to `950e18`. Bob's 50 KERNEL tokens have been silently consumed as fees with no revert, no event reflecting the true debit, and no recourse.
6. The emitted event `BridgedKernelToBSC(..., amount=1000e18, ...)` misrepresents the actual debit, making off-chain accounting incorrect. [6](#0-5)

### Citations

**File:** contracts/KERNEL/KernelVaultETH.sol (L183-186)
```text
        // Approve the Kernel OFT adapter to spend an unlimited amount of KERNEL tokens on behalf of this contract
        // for bridging purposes in order to avoid the need to approve the contract every time a bridging transaction
        // is initiated
        kernel.forceApprove(address(kernelOftAdapter), type(uint256).max);
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L193-195)
```text
    function depositKernel(uint256 amount) external nonReentrant whenNotPaused {
        _depositKernel(msg.sender, amount);
    }
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L250-266)
```text
        SendParam memory sendParam = SendParam({
            dstEid: dstLzChainId,
            to: getReceiver(),
            amountLD: amount,
            minAmountLD: minAmount,
            extraOptions: bytes(""),
            composeMsg: bytes(""),
            oftCmd: bytes("")
        });

        MessagingFee memory fee = MessagingFee({ nativeFee: nativeFee, lzTokenFee: 0 });

        lastBridgedDepositId = counter - 1;

        kernelOftAdapter.send{ value: nativeFee }(sendParam, fee, refundAddress);

        emit BridgedKernelToBSC(dstLzChainId, receiver, amount, minAmount, nativeFee, lastBridgedDepositId);
```

**File:** contracts/interfaces/IKERNEL_OFTAdapter.sol (L37-40)
```text
struct OFTReceipt {
    uint256 amountSentLD; // Amount of tokens ACTUALLY debited from the sender in local decimals
    uint256 amountReceivedLD; // Amount of tokens to be received on the remote side
}
```

**File:** contracts/L1Vault.sol (L240-240)
```text
        IERC20(address(rsETH)).safeIncreaseAllowance(address(oftAdapter), amount);
```
