### Title
Fee accidentally trapped in `ExternalActionSwap`/`LifiExternalAction` when `circomData.relay == address(0)` - (`contracts/external-actions/swaps/ExternalActionSwap.sol`)

### Summary
The claimed equality `sendToRelay(relay, amount, token)` transfers `amount` iff `relay != address(0) && amount > 0` is correct, per `Transferer.sendToRelay` [1](#0-0) . Tracing both call sites shows this is exploitable-by-omission in `ExternalActionSwap.swap` but is **not** exploitable in `EmporiumUpgradeable`, and the "harvestable by next caller" escalation to Critical/theft is not supported by the code.

### Finding Description
In `ExternalActionSwap.swap`, `totalFee` (`hinkalFee` plus `relayFee` when the fee token equals the output token) is unconditionally subtracted from `swappedAmount` to compute `amountToSendToHinkal`, regardless of whether `sendToRelay` actually moved any tokens: [2](#0-1) 

When `circomData.relay == address(0)` — which is fully permitted by `relayerIsValid` (only checked when `relay != address(0)`) and by `performHinkalChecks`'s alternative branch requiring `originalSender == sender` when `relay == address(0)` [3](#0-2)  and [4](#0-3)  — `sendToRelay` no-ops per `Transferer.sendToRelay`'s `relay != address(0)` guard. The `totalFee` tokens are never transferred out, yet they are excluded from `amountToSendToHinkal` that is sent back to `msg.sender` (Hinkal). The tokens remain stuck in the `ExternalActionSwap`/`LifiExternalAction` contract's balance. There is no sweep/rescue/withdraw function anywhere in `ExternalActionBaseV2` or its subclasses that could recover this balance [5](#0-4) , so this fee is permanently frozen in that contract, not merely "stranded until harvested."

By contrast, `EmporiumUpgradeable`'s equivalent path is not broken. `payRelay` returns early (no accounting side effect) when `relay == address(0)`, and the un-sent fee amount stays measured by `balancesAfter[i]` inside `runAction`'s `balanceChange` computation, which is subsequently paid back to the same depositor via `handleOut` as part of their own change UTXO: [6](#0-5) [7](#0-6) 
So in Emporium the unsent fee is not lost — it is returned to the original caller, which is the correct, self-consistent behavior for a self-relayed (relay=0) transaction. The claim that both `ExternalActionSwap.swap` and `EmporiumUpgradeable.payRelay` "guarantee the fee is retained by the action" is false for Emporium.

Additionally, the "harvestable by the next caller" escalation does not hold for `ExternalActionSwap` either. `LifiExternalAction.callRouter` measures `swappedAmount` as a fresh balance delta immediately around the router call: [8](#0-7) 
Any previously stranded balance is captured in `balanceBefore` and therefore subtracted out of the next `swappedAmount`, so it is not counted as an extra output for a subsequent swapper — it simply continues to sit unclaimed in the contract. No code path lets a second unprivileged caller withdraw this residual balance.

### Impact Explanation
- `ExternalActionSwap`/`LifiExternalAction`: fee tokens (`hinkalFee`, and `relayFee` when fee token == output token) become permanently locked in the action contract whenever a self-relayed swap (`relay == address(0)`) is submitted with a nonzero fee structure. This is a permanent freezing of protocol/relay fee funds, matching the **High** severity category ("theft or permanent freezing of protocol/relay fees"), not Critical, because no unprivileged party can subsequently extract the frozen balance.
- `EmporiumUpgradeable`: not vulnerable — the unsent fee is correctly returned to the depositor as change.

### Likelihood Explanation
Trivially reachable by any unprivileged caller: submit a valid `transact` through a registered `LifiExternalAction`/`ExternalActionSwap` action with `circomData.relay = address(0)`, `circomData.originalSender = msg.sender`, and a nonzero `feeStructure.flatFee`/`variableRate`. This requires no special role and is repeatable on every self-relayed swap, growing the stuck balance each time; the caller loses only their own designated fee amount (their own funds), they don't gain anything, and no other party can recover or claim it either.

### Recommendation
In `ExternalActionSwap.swap`, only deduct `totalFee` from `amountToSendToHinkal` for the portion actually transferred by `sendToRelay` (i.e., zero out the fee amounts that resulted in no-ops when `circomData.relay == address(0)`), or route them back into the amount sent to `msg.sender`/user instead of silently discarding them — mirroring the behavior already implemented correctly in `EmporiumUpgradeable`.

### Proof of Concept
Foundry test plan:
1. Deploy `LifiExternalAction` with a mock router, register it in `Hinkal`, whitelist as `allowedRecipient`.
2. Craft a `transact` call with `circomData.relay = address(0)`, `circomData.originalSender = msg.sender`, nonzero `feeStructure.flatFee`/`variableRate`, and a mock router that returns a fixed `outputToken` amount.
3. Assert: `IERC20(outputToken).balanceOf(lifiAction)` increases by exactly `totalFee` after the tx, while `amountToSendToHinkal` transferred to Hinkal equals `swappedAmount - totalFee` (confirms fee is neither sent to relay nor returned to caller).
4. Perform a second, unrelated swap on the same `outputToken` through the same action and assert the second caller's credited UTXO/output equals exactly their own `swappedAmount - totalFee` (not `swappedAmount - totalFee + firstStuckFee`), proving the residual balance is not harvestable — confirming the finding is "permanent freeze," not "theft via harvest."

### Citations

**File:** contracts/Transferer.sol (L178-190)
```text
    function sendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) internal {
        if (relay != address(0) && actualAmount > 0) {
            transferERC20TokenOrETH(
                erc20TokenAddress,
                relay,
                uint256(actualAmount)
            );
        }
    }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L78-97)
```text
        if (circomData.feeStructure.feeToken == outputToken) {
            sendToRelay(circomData.relay, relayFee + hinkalFee, outputToken);
        } else {
            sendToRelay(
                circomData.relay,
                relayFee,
                circomData.feeStructure.feeToken
            );
            sendToRelay(circomData.relay, hinkalFee, outputToken);
        }

        uint256 totalFee = hinkalFee +
            (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
        uint256 amountToSendToHinkal = swappedAmount - totalFee;

        transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);

        utxoSet = new UTXO[](1);
        utxoSet[0] = UTXO({
            amount: amountToSendToHinkal,
```

**File:** contracts/HinkalHelper.sol (L30-35)
```text
    function relayerIsValid(address relay) internal view {
        if (relay != address(0)) {
            require(tx.origin == relay, "Unauthorized relay");
            require(isRelayInList(relay), "Relay is not whitelisted");
        }
    }
```

**File:** contracts/HinkalHelper.sol (L213-219)
```text
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );
```

**File:** contracts/external-actions/ExternalActionBaseV2.sol (L1-43)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.17;

import {CircomData} from "../types/CircomData.sol";
import {UTXO} from "../types/UTXO.sol";
import {IExternalActionV2} from "../types/IExternalActionV2.sol";
import {OwnerHinkal} from "../OwnerHinkal.sol";

abstract contract ExternalActionBaseV2 is IExternalActionV2, OwnerHinkal {
    mapping(address => bool) internal isAllowedRecipient;

    /*
     * @dev Modifier to check if the sender is allowed to call the action
     * @dev Used to handle VolatileTokenAction and Hinkal interactions
     */
    modifier onlyAllowedRecipient() {
        require(
            isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }

    constructor(address[] memory _allowedRecipients) {
        for (uint i = 0; i < _allowedRecipients.length; i++) {
            isAllowedRecipient[_allowedRecipients[i]] = true;
        }
    }

    function setAllowedRecipients(
        address[] calldata recipients
    ) external onlyOwner {
        for (uint i = 0; i < recipients.length; i++) {
            require(recipients[i] != address(0), "zero address!");
            isAllowedRecipient[recipients[i]] = true;
        }
    }

    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external virtual returns (UTXO[] memory utxoSet) {}
}
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-149)
```text
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 balanceChange = int256(balancesAfter[i]) -
                int256(balancesBefore[i]);

            if (deltaAmountChanges[i] < 0) {
                balanceChange -= deltaAmountChanges[i];
                // this equation reads: total change of emporium balance = what was moved to emporium (-deltaAmountChange) + how emporium balance changed through tx (balanceChange)
            }

            // the only case when balanceChange can be < 0, when there were some funds on emporium before the call
            if (balanceChange < 0) {
                revert BalanceChangeShouldBePositive();
            }

            UTXO memory utxoOut = handleOut(balanceChange, circomData, i);

            if (utxoOut.amount > 0) {
                utxoSet[utxoSetLength++] = utxoOut;
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L262-282)
```text
    function payRelay(
        address relay,
        address signerAddress,
        uint256 relayFee,
        address erc20TokenAddress
    ) internal {
        if (relay == address(0) || relayFee == 0) {
            return;
        }

        if (signerAddress == address(0)) {
            sendToRelay(relay, relayFee, erc20TokenAddress);
        } else {
            sendToRelayFromWallet(
                relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }
    }
```

**File:** contracts/external-actions/swaps/LifiExternalAction.sol (L16-36)
```text
    function callRouter(
        address inputToken,
        uint256 inputAmount,
        address outputToken,
        bytes calldata externalActionMetadata
    ) internal override returns (uint256 swappedAmount) {
        uint256 balanceBefore = getERC20OrETHBalance(outputToken);

        if (inputToken == address(0)) {
            (bool success, ) = router.call{value: inputAmount}(
                externalActionMetadata
            );
            require(success, "LI.FI swap failed: native coin");
        } else {
            approveUnlimited(inputToken, router);
            (bool success, ) = router.call(externalActionMetadata);
            require(success, "LI.FI swap failed: erc-20 token");
        }

        swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore;
    }
```
