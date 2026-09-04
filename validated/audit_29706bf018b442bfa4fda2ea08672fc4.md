No sweep/withdraw function exists in `ExternalActionBaseV2`, `ExternalActionSwap`, or `LifiExternalAction`, so any residual fee balance stranded in the action contract has no on-chain recovery path.### Title
Fee is deducted from swap output but never sent to anyone when `relay == address(0)`, permanently freezing user funds - (File: `contracts/external-actions/swaps/ExternalActionSwap.sol`)

### Summary
`ExternalActionSwap.swap()` unconditionally subtracts `totalFee` (relay flat fee + Hinkal variable fee) from `swappedAmount` to compute `amountToSendToHinkal`, but only actually transfers that fee out via `sendToRelay` when `circomData.relay != address(0)`. When a user self-serves without a relay (`relay == address(0)`, which requires `originalSender == msg.sender` per `HinkalHelper.performHinkalChecks`), `sendToRelay` no-ops (`Transferer.sol:178-190`), yet the fee amount is still stripped from the credited UTXO. The stripped tokens remain stuck in the `LifiExternalAction`/`ExternalActionSwap` contract balance with no sweep/withdraw function anywhere in `ExternalActionBaseV2`, `ExternalActionSwap`, or `LifiExternalAction` to recover them.

### Finding Description
The broken equality: `amountToSendToHinkal` (and thus the credited UTXO) should equal `swappedAmount` minus fees that were *actually paid out*, i.e. `amountToSendToHinkal == swappedAmount - (fees actually transferred)`. Instead the code computes:

```solidity
// contracts/external-actions/swaps/ExternalActionSwap.sol:70-93
uint256 relayFee = circomData.feeStructure.flatFee;
uint256 hinkalFee = hinkalHelper.calculateRelayFee(swappedAmount, 0, circomData.feeStructure.variableRate);

if (circomData.feeStructure.feeToken == outputToken) {
    sendToRelay(circomData.relay, relayFee + hinkalFee, outputToken);
} else {
    sendToRelay(circomData.relay, relayFee, circomData.feeStructure.feeToken);
    sendToRelay(circomData.relay, hinkalFee, outputToken);
}

uint256 totalFee = hinkalFee + (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
uint256 amountToSendToHinkal = swappedAmount - totalFee;

transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);
```

`sendToRelay` (`contracts/Transferer.sol:178-190`) is a no-op whenever `relay == address(0)`:
```solidity
function sendToRelay(address relay, uint256 actualAmount, address erc20TokenAddress) internal {
    if (relay != address(0) && actualAmount > 0) {
        transferERC20TokenOrETH(erc20TokenAddress, relay, uint256(actualAmount));
    }
}
```

Per `HinkalHelper.performHinkalChecks` (`contracts/HinkalHelper.sol:213-219`), `relay == address(0)` is only legal when `circomData.originalSender == sender` (the caller uses no relay and submits their own transaction) — this is a normal, unprivileged, reachable path, not an edge case reserved for privileged roles.

In that self-serve path, `totalFee` is still computed and subtracted from `amountToSendToHinkal`, but `sendToRelay` transfers nothing. The difference (`swappedAmount - amountToSendToHinkal == totalFee`) simply remains as ERC20/ETH balance sitting in the `LifiExternalAction` contract. Contrast this with `_internalTransact` in `Hinkal.sol:172-230`, which explicitly guards fee computation with `if (circomData.relay != address(0))` so no fee is charged when there is no relay, and with `EmporiumUpgradeable.runAction`/`handleOut`, where the UTXO amount is derived from the *actual* balance delta after `payRelayFees` runs — if `payRelay` no-ops (relay == 0), the funds are never removed from the balance and thus flow back into the user's UTXO. `ExternalActionSwap.swap()` does not follow this pattern; it hardcodes the fee subtraction independent of whether the transfer occurred.

There is no sweep, rescue, or withdraw function in `ExternalActionBaseV2.sol`, `ExternalActionSwap.sol`, or `LifiExternalAction.sol` to recover this stranded balance, so once stuck, it is permanently unrecoverable by anyone — not the user, not the protocol, not the relay.

### Impact Explanation
Every time a user performs a LiFi swap through Hinkal without using a relay (self-serve/no-relay transaction, a normal and fully attacker-reachable mode), the flat relay fee and/or Hinkal variable fee computed from the real swap output is deducted from the credited UTXO but never delivered anywhere — it is permanently locked in the `LifiExternalAction` contract's token balance with no code path to retrieve it. This is a permanent loss of value for the user (the fee is charged but nothing is received in return, and no relay/protocol collects it either), matching "permanent freezing of user funds" (Critical) or, viewed as intended relay/protocol revenue that never gets collected and can never be swept, "permanent freezing of protocol/relay fees" (High). This is repeatable on every self-relay LiFi swap and scales with swap volume; the loss is proportional to `feeStructure.flatFee` and `variableRate` applied to `swappedAmount` on each such transaction.

### Likelihood Explanation
No privileged role or third-party cooperation is required. Any unprivileged user can trigger this simply by calling `Hinkal.transact` for a LiFi swap action with `circomData.relay == address(0)` and `circomData.originalSender == msg.sender` (the legitimate self-serve path explicitly allowed by `performHinkalChecks`), and any non-zero `feeStructure.flatFee`/`variableRate`. No special CIRCOM_P boundary value, no router manipulation, and no proof forgery is needed — this triggers on the ordinary, documented control-flow branch. The only precondition is that the fee structure fields are non-zero, which is attacker/prover-controlled input in `CircomData.feeStructure`.

### Recommendation
Make the fee deduction conditional on actual fee delivery, mirroring `_internalTransact`'s pattern: when `circomData.relay == address(0)`, skip the relay-fee portion entirely (set `relayFee = 0`) so it flows back to the user via `amountToSendToHinkal`, or restructure `swap()` to compute `amountToSendToHinkal` from the *actual* balance delta after fee transfers (as `EmporiumUpgradeable.handleOut` does), rather than subtracting a fee that may never have actually left the contract.

### Proof of Concept
Foundry test plan:
1. Deploy `LifiExternalAction` with a mock router that, given `externalActionMetadata`, transfers a fixed `swappedAmount` of `outputToken` to the action contract (simulating a successful LI.FI swap).
2. Register `LifiExternalAction` in `Hinkal` via `registerExternalAction`, set `allowedRecipients`.
3. Build a `CircomData` for a swap: `relay = address(0)`, `originalSender = attacker`, non-zero `feeStructure.flatFee` and `feeStructure.variableRate`, valid `amountChanges`/nullifiers/commitments and a locally generated proof satisfying `performHinkalChecks`/`verifyProof`.
4. Call `Hinkal.transact(...)` as `attacker` (msg.sender == originalSender, satisfying the no-relay branch).
5. Assert:
   - `amountToSendToHinkal` returned as the UTXO amount `== swappedAmount - totalFee` (confirms fee was deducted).
   - `LifiExternalAction`'s balance of `outputToken` after the call `== totalFee` (fee tokens stuck in the contract, not sent to relay since `relay == address(0)`, not returned to user).
   - No function on `LifiExternalAction`/`ExternalActionBaseV2`/`OwnerHinkal` can move that residual balance out (grep confirms no `withdraw`/`sweep`/`rescue` function exists).
   - Repeat the swap multiple times to show the stranded balance accumulates monotonically, confirming permanent, compounding loss. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L70-101)
```text
        uint256 relayFee = circomData.feeStructure.flatFee;

        uint256 hinkalFee = hinkalHelper.calculateRelayFee(
            swappedAmount,
            0,
            circomData.feeStructure.variableRate
        );

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
            erc20Address: outputToken,
            stealthAddressStructure: circomData.stealthAddressStructure,
            timeStamp: block.timestamp
        });
```

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

**File:** contracts/HinkalHelper.sol (L208-219)
```text
    function performHinkalChecks(
        CircomData calldata circomData,
        Dimensions calldata dimensions,
        address sender
    ) external view returns (uint256[] memory) {
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );
```

**File:** contracts/Hinkal.sol (L172-230)
```text
    function _internalTransact(CircomData calldata circomData) private {
        bool hasPaidToRelay = false;
        for (uint64 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 deltaAmountChange = _calculateDeltaAmount(circomData, i);

            if (deltaAmountChange > 0) {
                require(
                    circomData.externalActionData.externalAddress == msg.sender,
                    "Deposit should come from the sender"
                );
                transferERC20TokenFromOrCheckETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    address(this),
                    uint256(circomData.amountChanges[i])
                );
            } else {
                uint256 sumAbs = uint256(-deltaAmountChange);
                uint256 relayFee = 0;
                if (circomData.relay != address(0)) {
                    uint256 flatFee = circomData.feeStructure.feeToken ==
                        circomData.erc20TokenAddresses[i]
                        ? circomData.feeStructure.flatFee
                        : 0;

                    require(
                        sumAbs >= flatFee,
                        "Relay Fee is over withdraw amount"
                    );

                    uint256 recipientAmount = ((10000 -
                        circomData.feeStructure.variableRate) *
                        (sumAbs - flatFee)) / 10000;

                    relayFee = sumAbs - recipientAmount;

                    if (relayFee > 0) {
                        transferERC20TokenOrETH(
                            circomData.erc20TokenAddresses[i],
                            circomData.relay,
                            relayFee
                        );
                    }
                    hasPaidToRelay = true;
                }
                if (sumAbs - relayFee > 0) {
                    transferERC20TokenOrETH(
                        circomData.erc20TokenAddresses[i],
                        circomData.externalActionData.externalAddress,
                        sumAbs - relayFee
                    );
                }
            }
        }
        require(
            circomData.relay == address(0) || hasPaidToRelay,
            "relay not paid"
        );
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-184)
```text
        payRelayFees(circomData, stack.signerAddress, deltaAmountChanges);

        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        UTXO[] memory utxoSet = new UTXO[](
            circomData.erc20TokenAddresses.length
        );

        uint256 utxoSetLength;

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
            }
        }

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
        }

        return utxoSet;
    }

    function handleOut(
        int256 balanceChange,
        CircomData calldata circomData,
        uint256 i
    ) internal returns (UTXO memory outUtxo) {
        // total change can be less than zero if there was some balance before the call -> that's why we have <=
        if (balanceChange <= 0) {
            return outUtxo;
        }

        transferERC20TokenOrETH(
            circomData.erc20TokenAddresses[i],
            msg.sender,
            uint256(balanceChange)
        );

        outUtxo = UTXO(
            uint256(balanceChange),
            circomData.erc20TokenAddresses[i],
            circomData.stealthAddressStructure,
            circomData.timeStamp
        );
    }
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

**File:** contracts/external-actions/swaps/LifiExternalAction.sol (L1-37)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.17;

import "./ExternalActionSwap.sol";

contract LifiExternalAction is ExternalActionSwap {
    constructor(
        address _hinkalHelper,
        address _wrapper,
        address _router,
        address[] memory _allowedRecipients
    )
        ExternalActionSwap(_hinkalHelper, _wrapper, _router, _allowedRecipients)
    {}

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
}
```
