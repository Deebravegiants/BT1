### Title
Native ETH permanently frozen in `KernelVaultETH` due to under-constrained fee check and absent ETH rescue mechanism - (File: contracts/KERNEL/KernelVaultETH.sol)

### Summary
`KernelVaultETH.bridgeKernelToBSC()` accepts any `msg.value >= nativeFee` but only forwards exactly `nativeFee` to the OFT adapter. The surplus `msg.value - nativeFee` is permanently trapped because the contract has no `receive()` function, no `recoverETH()` function, and no other path to withdraw native ETH.

### Finding Description
In `bridgeKernelToBSC()`, the native-fee guard is:

```solidity
if (msg.value < nativeFee) {
    revert InsufficientNativeFee();
}
``` [1](#0-0) 

This permits `msg.value > nativeFee`. However, the call to the OFT adapter forwards only `nativeFee`:

```solidity
kernelOftAdapter.send{ value: nativeFee }(sendParam, fee, refundAddress);
``` [2](#0-1) 

The `refundAddress` argument is the LayerZero refund target for the OFT adapter itself — it does not cause the adapter to return the unforwarded surplus back to the caller. The difference `msg.value - nativeFee` stays in `KernelVaultETH`.

The contract inherits only `AccessControlUpgradeable`, `PausableUpgradeable`, and `ReentrancyGuardUpgradeable` — none of which provide ETH recovery. [3](#0-2)  There is no `receive()` function, no `recoverETH()` / `rescueETH()` function, and no other payable function that could drain the balance. [4](#0-3) 

This is the direct analog of the reported `FeeBuyback` issue: a contract that accepts native ETH via `msg.value` in an external call path but provides no mechanism to rescue the resulting leftover.

### Impact Explanation
Any ETH sent in excess of `nativeFee` is permanently frozen inside `KernelVaultETH`. Because the contract has no ETH-withdrawal path whatsoever, recovery is impossible without a contract upgrade. This constitutes **permanent freezing of funds**.

### Likelihood Explanation
`bridgeKernelToBSC()` is restricted to `OPERATOR_ROLE`. [5](#0-4)  The realistic trigger is an operator who over-estimates the fee (e.g., the on-chain fee drops between the `getNativeFee()` quote and the actual submission, or the operator adds a safety buffer). The check explicitly allows this: `msg.value < nativeFee` is the only guard, so any over-payment silently succeeds and the surplus is lost. The likelihood is **low** (trusted operator, accidental over-payment), but the consequence is irreversible.

### Recommendation
1. **Preferred fix**: Replace the under-constrained check with an exact equality check, mirroring the pattern used in every other bridge contract in the repository (e.g., `TACWETHBridge` uses `if (msg.value != nativeFee) revert InvalidNativeFee()`): [6](#0-5) 
   ```solidity
   if (msg.value != nativeFee) revert IncorrectNativeFee();
   ```
2. **Defensive fallback**: Add an admin-only `recoverETH()` function (following the pattern already present in `Recoverable.sol`) so that any accidentally trapped ETH can be rescued. [7](#0-6) 

### Proof of Concept
1. Operator calls `getNativeFee(amount, minAmount)` and receives `0.005 ETH`.
2. Operator submits `bridgeKernelToBSC(amount, minAmount, 0.005 ether, refundAddress)` with `msg.value = 0.01 ether` (intentional safety buffer or stale quote).
3. The check `msg.value < nativeFee` → `0.01 < 0.005` is **false**, so execution continues.
4. `kernelOftAdapter.send{ value: 0.005 ether }(...)` is called; only `0.005 ETH` leaves the contract.
5. The remaining `0.005 ETH` sits in `KernelVaultETH.balance` permanently — no function exists to withdraw it. [8](#0-7)

### Citations

**File:** contracts/KERNEL/KernelVaultETH.sol (L21-21)
```text
contract KernelVaultETH is Initializable, AccessControlUpgradeable, PausableUpgradeable, ReentrancyGuardUpgradeable {
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L193-267)
```text
    function depositKernel(uint256 amount) external nonReentrant whenNotPaused {
        _depositKernel(msg.sender, amount);
    }

    /**
     * @notice Deposits KERNEL tokens into the vault on behalf of a user
     * @param user The address of the user
     * @param amount The amount of KERNEL tokens to deposit
     */
    function depositKernelFor(
        address user,
        uint256 amount
    )
        external
        nonReentrant
        whenNotPaused
        onlyRole(MERKLE_DISTRIBUTOR_ROLE)
    {
        _depositKernel(user, amount);
    }

    /*//////////////////////////////////////////////////////////////
                            Operator Actions
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Bridges KERNEL tokens to the BSC chain
     * @param amount The amount of KERNEL tokens to bridge
     * @param minAmount The minimum amount of KERNEL tokens to receive on BSC
     * @param nativeFee The native fee to pay for the bridge
     * @param refundAddress The address to refund the native fee to in case of a failed bridge transaction
     */
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

**File:** contracts/bridges/TACWETHBridge.sol (L111-113)
```text
        if (msg.value != nativeFee) {
            revert InvalidNativeFee();
        }
```

**File:** contracts/utils/Recoverable.sol (L64-73)
```text
    function recoverETH(address recipient, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(recipient);
        if (amount == 0) revert ZeroAmount();
        if (address(this).balance < amount) revert InsufficientBalance();

        (bool success,) = payable(recipient).call{ value: amount }("");
        if (!success) revert TransferFailed();

        emit ETHRecovered(recipient, amount);
    }
```
