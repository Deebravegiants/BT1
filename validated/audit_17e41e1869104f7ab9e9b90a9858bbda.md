### Title
`KernelVaultETH::bridgeKernelToBSC` Does Not Refund Excess Native Fee to Caller - (`contracts/KERNEL/KernelVaultETH.sol`)

---

### Summary

`KernelVaultETH::bridgeKernelToBSC` uses a less-than check (`msg.value < nativeFee`) instead of a strict equality check (`msg.value != nativeFee`). This allows the caller to send more ETH than required. Only exactly `nativeFee` is forwarded to the LayerZero OFT adapter; the excess `msg.value - nativeFee` is permanently trapped in the contract with no recovery mechanism.

---

### Finding Description

In `contracts/KERNEL/KernelVaultETH.sol`, the `bridgeKernelToBSC` function validates the native fee as follows:

```solidity
if (msg.value < nativeFee) {
    revert InsufficientNativeFee();
}
``` [1](#0-0) 

It then forwards only exactly `nativeFee` to the OFT adapter:

```solidity
kernelOftAdapter.send{ value: nativeFee }(sendParam, fee, refundAddress);
``` [2](#0-1) 

Any ETH in excess of `nativeFee` (i.e., `msg.value - nativeFee`) remains in the `KernelVaultETH` contract. The contract has no ETH withdrawal function and no `receive()` fallback, so this excess is permanently frozen.

This is in direct contrast to every other bridge function in the codebase, which all enforce strict equality:

- `L1VaultV2::bridgeRsETHToL2`: `if (msg.value != nativeFee) revert IncorrectNativeFee();` [3](#0-2) 

- `RSETHPoolV3ExternalBridge::bridgeAssets`: `if (msg.value != nativeFee) revert IncorrectNativeFee();` [4](#0-3) 

- `RSETHPoolNoWrapper::bridgeAssets`: `if (msg.value != nativeFee) revert IncorrectNativeFee();` [5](#0-4) 

The `KernelVaultETH` contract has no ETH recovery path — no `withdrawETH`, no `Recoverable` mixin, and no `receive()` function. [6](#0-5) 

---

### Impact Explanation

Any ETH sent in excess of `nativeFee` is permanently frozen inside `KernelVaultETH`. There is no function to recover it. This constitutes **permanent freezing of funds** for the operator who sent the excess ETH.

**Impact: Medium — Permanent freezing of unclaimed/excess native ETH.**

---

### Likelihood Explanation

The `bridgeKernelToBSC` function is callable by the `OPERATOR_ROLE`. The operator is a legitimate protocol participant who routinely calls `getNativeFee` to estimate the required fee and then submits the bridge transaction. Due to LayerZero fee fluctuations between the quote and the submission, or a simple off-by-one mistake, the operator may send slightly more ETH than `nativeFee`. The `<` check silently accepts this overpayment and traps the excess permanently.

**Likelihood: Medium** — Normal operational conditions (fee estimation lag, manual transaction submission) make this a realistic scenario.

---

### Recommendation

Replace the less-than check with a strict equality check, consistent with all other bridge functions in the codebase:

```solidity
// Before
if (msg.value < nativeFee) {
    revert InsufficientNativeFee();
}

// After
if (msg.value != nativeFee) {
    revert IncorrectNativeFee();
}
``` [1](#0-0) 

---

### Proof of Concept

1. Operator calls `getNativeFee(amount, minAmount)` → returns `X` wei.
2. Due to a LayerZero fee update between the quote and submission, the operator sends `msg.value = X + 0.01 ETH` to be safe.
3. `bridgeKernelToBSC` check: `msg.value < nativeFee` → `X + 0.01 ETH < X` → **false**, so no revert.
4. `kernelOftAdapter.send{ value: nativeFee }(...)` forwards only `X` wei.
5. The excess `0.01 ETH` remains in `KernelVaultETH` with no withdrawal path.
6. The excess ETH is permanently frozen. [6](#0-5)

### Citations

**File:** contracts/KERNEL/KernelVaultETH.sol (L225-267)
```text
    function bridgeKernelToBSC(
        uint256 amount,
        uint256 minAmount,
        uint256 nativeFee,
        address refundAddress
    )
        external
        payable
        nonReentrant
        onlyRole(OPERATOR_ROLE)
    {
        UtilLib.checkNonZeroAddress(refundAddress);

        if (kernel.balanceOf(address(this)) < amount) {
            revert InsufficientKernelBalance();
        }

        if (minAmount > amount || minAmount == 0) {
            revert InvalidMinAmount();
        }

        if (msg.value < nativeFee) {
            revert InsufficientNativeFee();
        }

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
    }
```

**File:** contracts/L1VaultV2.sol (L314-316)
```text
        if (msg.value != nativeFee) {
            revert IncorrectNativeFee();
        }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L689-691)
```text
        if (msg.value != nativeFee) {
            revert IncorrectNativeFee();
        }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L469-471)
```text
        if (msg.value != nativeFee) {
            revert IncorrectNativeFee();
        }
```
