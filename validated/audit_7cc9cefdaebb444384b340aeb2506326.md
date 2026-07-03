### Title
`BridgedRsETHToL2` Event Emits Unadjusted `amount` Instead of Actual `amountSentLD` After OFT Dust Removal — (`contracts/L1VaultV2.sol`)

### Summary

`L1VaultV2.bridgeRsETHToL2` ignores the `OFTReceipt` returned by `oftAdapter.send()` and unconditionally emits the caller-supplied `amount` in the `BridgedRsETHToL2` event, even when the OFT adapter silently debits a dust-adjusted (smaller) amount due to shared-decimal rounding.

### Finding Description

In `bridgeRsETHToL2`, the return value of `oftAdapter.send()` is discarded: [1](#0-0) 

```solidity
oftAdapter.send{ value: nativeFee }(sendParam, fee, msg.sender);
emit BridgedRsETHToL2(dstLzChainId, l2Receiver, amount, minAmount);
```

The `IRSETH_OFTAdapter.send` (and the mirrored `IOFT.send`) returns an `OFTReceipt` containing the **actual** debited amount: [2](#0-1) 

```solidity
struct OFTReceipt {
    uint256 amountSentLD;    // Amount ACTUALLY debited
    uint256 amountReceivedLD;
}
```

LayerZero OFT adapters apply a `_removeDust` step during `_debitView`: any sub-`sharedDecimal` wei in `amountLD` is truncated and left in the adapter. For rsETH (18 decimals) with a typical `sharedDecimals = 6`, up to `10^12` wei per call can be silently retained. The `minAmountLD` guard only prevents the transaction from reverting if the dust-adjusted amount falls below `minAmount`; it does not prevent the event from logging the wrong value.

The event therefore always logs the original `amount` argument, not `oftReceipt.amountSentLD`.

### Impact Explanation

- Off-chain indexers and monitoring systems that rely on `BridgedRsETHToL2` will record a higher bridged amount than was actually transferred cross-chain.
- Residual dust accumulates in the OFT adapter with no recovery path visible in the in-scope contracts.
- **L2 minting is not affected** — the LayerZero protocol delivers `amountReceivedLD` to L2 independently of the L1 event, so no L2 supply divergence occurs at the protocol level. The impact is confined to off-chain accounting and observability.

This matches the **Low** scope: *Contract fails to deliver promised returns, but doesn't lose value.*

### Likelihood Explanation

Dust removal is a deterministic, always-on behavior of the OFT standard whenever `amountLD % (10^(localDecimals - sharedDecimals)) != 0`. For rsETH with 18 local / 6 shared decimals, any amount not divisible by `10^12` triggers it. This is a routine condition in normal operation.

### Recommendation

Capture and use the return value of `oftAdapter.send()`:

```solidity
(, OFTReceipt memory oftReceipt) = oftAdapter.send{ value: nativeFee }(sendParam, fee, msg.sender);
emit BridgedRsETHToL2(dstLzChainId, l2Receiver, oftReceipt.amountSentLD, minAmount);
```

This ensures the emitted amount matches what was actually debited and cross-chain-transferred.

### Proof of Concept

1. Deploy a mock `IRSETH_OFTAdapter` whose `send()` returns `amountSentLD = _sendParam.amountLD - 1` (simulating 1-wei dust removal).
2. Call `bridgeRsETHToL2(1e18, 0.9e18, nativeFee)`.
3. Observe that the `BridgedRsETHToL2` event logs `amount = 1e18`, while `oftReceipt.amountSentLD = 1e18 - 1`.
4. Assert `event.amount != oftReceipt.amountSentLD` — the invariant is broken. [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/L1VaultV2.sol (L292-335)
```text
    function bridgeRsETHToL2(
        uint256 amount,
        uint256 minAmount,
        uint256 nativeFee
    )
        external
        payable
        nonReentrant
        onlyRole(MANAGER_ROLE)
    {
        if (bridgeType != BridgeType.LayerZero) {
            revert InactiveBridgeType();
        }

        if (rsETH.balanceOf(address(this)) < amount) {
            revert InsufficientRsETHBalance();
        }

        if (minAmount > amount || minAmount == 0) {
            revert InvalidMinAmount();
        }

        if (msg.value != nativeFee) {
            revert IncorrectNativeFee();
        }

        IERC20(address(rsETH)).safeIncreaseAllowance(address(oftAdapter), amount);

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

        oftAdapter.send{ value: nativeFee }(sendParam, fee, msg.sender);

        emit BridgedRsETHToL2(dstLzChainId, l2Receiver, amount, minAmount);
    }
```

**File:** contracts/interfaces/IRSETH_OFTAdapter.sol (L37-40)
```text
struct OFTReceipt {
    uint256 amountSentLD; // Amount of tokens ACTUALLY debited from the sender in local decimals
    uint256 amountReceivedLD; // Amount of tokens to be received on the remote side
}
```

**File:** contracts/external/layerzero/interfaces/IOFT.sol (L37-59)
```text
struct OFTReceipt {
    uint256 amountSentLD; // Amount of tokens ACTUALLY debited from the sender in local decimals
    uint256 amountReceivedLD; // Amount of tokens to be received on the remote side
}

/// @title IOFT interface
/// @notice Interface for the token contracts following the OFT standard from LayerZero
interface IOFT {
    /// @notice Sends tokens to another chain
    /// @dev This function handles the cross-chain token transfer
    /// @param _sendParam Parameters for the send operation
    /// @param _fee Messaging fee for the LayerZero protocol
    /// @param _refundAddress Address to refund excess fees
    /// @return msgReceipt Receipt of the messaging operation
    /// @return oftReceipt Receipt of the OFT operation
    function send(
        SendParam calldata _sendParam,
        MessagingFee calldata _fee,
        address _refundAddress
    )
        external
        payable
        returns (MessagingReceipt memory msgReceipt, OFTReceipt memory oftReceipt);
```
