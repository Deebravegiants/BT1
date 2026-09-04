### Title
Protocol fee is permanently burned when `feeRecipient` is set to the zero address in `HinkalWrapper::_settleFee` - (File: `contracts/HinkalWrapper.sol`)

### Summary
`HinkalWrapper.prooflessDeposit` accepts a fully caller-supplied `ProoflessFeeStructure` (containing `feeRecipient`, `feeToken`, `feeAmount`) with no signature or on-chain validation tying it to the intended fee-collecting party (e.g. the dApp/relay operating the wrapper). `_settleFee` unconditionally forwards `feeAmount` to `feeStructure.feeRecipient` without ever checking that the recipient is non-zero, mirroring exactly the `GaugeProxy::distributeToken` pattern in the external report where an unset/zero recipient causes the fee to be burned instead of delivered.

### Finding Description
`HinkalWrapper.prooflessDeposit` calls `_settleFee(feeStructure)` before forwarding the deposit to `Hinkal`: [1](#0-0) 

`_settleFee` transfers the fee (ETH via `transferETH`, or ERC20 via `transferERC20TokenFrom`) directly to `feeStructure.feeRecipient` with no guard against `address(0)`: [2](#0-1) 

`feeStructure` is a plain `calldata` struct passed by the caller of `prooflessDeposit`, which is an unrestricted `external` function - no signer/relay authorization is required, and it is not covered by `calldataHash`/`signedMessageHash` or any other integrity check: [3](#0-2) 

`transferETH` performs a raw `call` that succeeds even when the target is `address(0)`, so ETH sent there is permanently burned rather than reverting: [4](#0-3) 

Any unprivileged EOA calling `HinkalWrapper.prooflessDeposit` can set `feeStructure.feeRecipient = address(0)` while still supplying the required `feeAmount` (the `require(msg.value >= feeStructure.feeAmount, ...)` check for ETH, or the ERC20 `transferFrom`, still executes and pulls the fee from the caller). The fee amount is still deducted from the depositor exactly as intended, but instead of reaching the dApp/relay operator that should collect it, it is sent to the zero address and permanently lost. This is functionally identical to the reported `GaugeProxy::distributeToken` bug: a fee-recipient value that can be zero is used in a transfer with no zero-address check, resulting in the fee being burned instead of collected.

### Impact Explanation
This causes permanent loss/freezing of the protocol/relay fee that the wrapper is designed to collect on behalf of the dApp operator. The depositor's cost is unchanged (they still pay the fee amount), so there is no incentive against doing this, and no privileged role is required to trigger it - matching the "High: theft or permanent freezing of protocol/relay fees" impact bucket.

### Likelihood Explanation
Low-to-medium: it requires a caller of `HinkalWrapper.prooflessDeposit` to deliberately (or through a misconfigured/buggy frontend) submit `feeRecipient = address(0)`. Since the field is entirely attacker-controlled `calldata` with no on-chain enforcement of a canonical/expected recipient, this requires no special access and can be triggered in a single transaction.

### Recommendation
In `_settleFee`, require `feeStructure.feeRecipient != address(0)` before performing the ETH or ERC20 transfer (or, more robustly, hardcode/whitelist the expected fee recipient in `HinkalWrapper` rather than trusting caller-supplied calldata), mirroring the recommendation from the referenced report of checking the recipient is non-zero before transferring the fee.

### Proof of Concept
1. Attacker (any EOA) calls `HinkalWrapper.prooflessDeposit(erc20Addresses, amounts, stealthAddressStructures, onChainEncryptedOutputs, createBlockedUtxos, feeStructure, orderId)` with `feeStructure.feeToken = address(0)`, `feeStructure.feeAmount = X`, `feeStructure.feeRecipient = address(0)`, and `msg.value = X + depositAmount`.
2. `_settleFee` computes `ethForHinkal = msg.value - X` and calls `transferETH(address(0), X)`, which succeeds (raw `call` to `address(0)` returns `success = true`), burning `X` ETH permanently. [5](#0-4) 
3. The remaining deposit flow proceeds normally via `IHinkal(hinkal).prooflessDeposit`, so the transaction succeeds end-to-end while the intended fee recipient (the wrapper's operator/relay) never receives its `X` fee.

### Citations

**File:** contracts/HinkalWrapper.sol (L28-47)
```text
    function prooflessDeposit(
        address[] calldata erc20Addresses,
        uint256[] calldata amounts,
        StealthAddressStructure[] calldata stealthAddressStructures,
        bytes[] calldata onChainEncryptedOutputs,
        bool createBlockedUtxos,
        ProoflessFeeStructure calldata feeStructure,
        string calldata orderId
    ) external payable {
        uint256 ethForHinkal = _settleFee(feeStructure);
        _pullAndApproveDepositTokens(erc20Addresses, amounts);
        IHinkal(hinkal).prooflessDeposit{value: ethForHinkal}(
            erc20Addresses,
            amounts,
            stealthAddressStructures,
            onChainEncryptedOutputs,
            createBlockedUtxos,
            orderId
        );
    }
```

**File:** contracts/HinkalWrapper.sol (L49-70)
```text
    function _settleFee(
        ProoflessFeeStructure calldata feeStructure
    ) internal returns (uint256 ethForHinkal) {
        ethForHinkal = msg.value;
        if (feeStructure.feeToken == address(0)) {
            require(
                msg.value >= feeStructure.feeAmount,
                "insufficient ETH for fee"
            );
            ethForHinkal = msg.value - feeStructure.feeAmount;
            if (feeStructure.feeAmount > 0) {
                transferETH(feeStructure.feeRecipient, feeStructure.feeAmount);
            }
        } else if (feeStructure.feeAmount > 0) {
            transferERC20TokenFrom(
                feeStructure.feeToken,
                msg.sender,
                feeStructure.feeRecipient,
                feeStructure.feeAmount
            );
        }
    }
```

**File:** contracts/types/ProoflessFeeStructure.sol (L1-8)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.6;

struct ProoflessFeeStructure {
    address feeRecipient;
    address feeToken;
    uint256 feeAmount;
}
```

**File:** contracts/TransfererBase.sol (L10-13)
```text
    function transferETH(address _recepient, uint256 _value) internal {
        (bool success, ) = _recepient.call{value: _value}("");
        require(success, "Transfer Failed");
    }
```
