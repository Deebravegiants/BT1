The code is clear. Let me confirm the key facts:

1. `bridgeKernelToBSC` is `payable` and checks `msg.value < nativeFee` (allows overpayment) [1](#0-0) 
2. It forwards **exactly** `nativeFee` to the OFT adapter, leaving any excess in the contract [2](#0-1) 
3. The contract has **no** `receive()`, `fallback()`, `recoverETH`, `sweep`, or any ETH withdrawal function — confirmed by grep and full file read [3](#0-2) 

---

### Title
Excess ETH sent to `bridgeKernelToBSC()` is permanently locked with no recovery path — (`contracts/KERNEL/KernelVaultETH.sol`)

### Summary
`bridgeKernelToBSC` accepts `msg.value >= nativeFee` but only forwards exactly `nativeFee` to the OFT adapter. Any excess ETH (`msg.value - nativeFee`) is retained by the contract permanently, as no `receive()`, `fallback()`, or ETH-recovery function exists.

### Finding Description
The guard at line 246 only rejects underpayment:

```solidity
if (msg.value < nativeFee) {
    revert InsufficientNativeFee();
}
```

The send at line 264 forwards only the declared fee:

```solidity
kernelOftAdapter.send{ value: nativeFee }(sendParam, fee, refundAddress);
```

The difference `msg.value - nativeFee` is silently retained by the vault. The contract has no `receive()` function, no `fallback()`, and no admin/operator function to recover native ETH. The file ends at line 398 with `_depositKernel` — no sweep or recovery exists anywhere in the contract.

### Impact Explanation
Every overpayment by the operator permanently locks ETH in the vault. Repeated bridge operations with even minor overpayments (e.g., due to fee estimation rounding, gas price changes, or operator error) accumulate locked ETH with zero withdrawal path. This constitutes a permanent freeze of protocol-owned native funds.

**Scope match:** Low — Contract fails to deliver promised returns (excess fee is not refunded), but doesn't lose user value.

### Likelihood Explanation
The operator is a trusted role, but overpayment is realistic:
- Fee estimates from `getNativeFee()` may be stale by the time the tx is submitted.
- Operators may intentionally pad `msg.value` to avoid `InsufficientNativeFee` reverts.
- The contract's own check explicitly permits `msg.value > nativeFee` with no refund logic.

### Recommendation
Add a refund of excess ETH at the end of `bridgeKernelToBSC`:

```solidity
uint256 excess = msg.value - nativeFee;
if (excess > 0) {
    (bool ok, ) = refundAddress.call{value: excess}("");
    require(ok, "ETH refund failed");
}
```

Alternatively, enforce exact payment: `if (msg.value != nativeFee) revert`.

### Proof of Concept
```solidity
// Operator calls with double the required fee
uint256 fee = vault.getNativeFee(amount, minAmount);
vault.bridgeKernelToBSC{value: fee * 2}(amount, minAmount, fee, refundAddress);

// Assert excess is locked
assert(address(vault).balance == fee);

// Confirm no recovery path exists
// (no recoverETH, no sweep, no receive/fallback in KernelVaultETH.sol)
```

### Citations

**File:** contracts/KERNEL/KernelVaultETH.sol (L246-248)
```text
        if (msg.value < nativeFee) {
            revert InsufficientNativeFee();
        }
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L264-264)
```text
        kernelOftAdapter.send{ value: nativeFee }(sendParam, fee, refundAddress);
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L382-398)
```text
    function _depositKernel(address user, uint256 amount) internal {
        UtilLib.checkNonZeroAddress(user);

        if (amount < minDeposit) {
            revert DepositAmountTooLow();
        }

        kernel.safeTransferFrom(msg.sender, address(this), amount);

        uint256 depositId = counter;

        userDeposits[depositId] = UserDeposit({ user: user, amount: amount });
        ++counter;

        emit KernelVaultETHDeposit(depositId, user, amount);
    }
}
```
