### Title
Unspent input tokens from LI.FI swaps are permanently stranded in `LifiExternalAction` with no refund path - ([File: contracts/external-actions/swaps/LifiExternalAction.sol])

### Summary
In the LI.FI swap external action, the full `inputAmount` pulled from `Hinkal` is transferred/approved to the `LifiExternalAction` contract before the router call, but the contract only measures and forwards the **output** token delta; it never checks whether the router actually consumed the entire `inputAmount`. Any unspent input token remains stuck in the contract with no code path to return it to the user, mirroring the wfCash "residual not sent back" bug class from the external report.

### Finding Description
`ExternalActionSwap.swap()` receives `inputAmount = -deltaAmounts[0]`, the exact amount that `Hinkal._externalTransact` transferred out of the vault to this external-action contract: [1](#0-0) 

`LifiExternalAction.callRouter` then either forwards the full native value or grants an unlimited approval and calls the LI.FI router with attacker/relayer-supplied `externalActionMetadata`, and computes `swappedAmount` solely from the **output** token balance delta: [2](#0-1) 

Back in `ExternalActionSwap.swap()`, only `swappedAmount` (output token) is used to compute fees and the amount forwarded to `msg.sender` (Hinkal); there is no equivalent accounting or forwarding step for the **input** token: [3](#0-2) 

If the LI.FI route does not consume the entire approved/forwarded `inputAmount` (e.g. partial-fill routing, refund-to-caller behavior in the aggregated DEX/bridge call, or dust left after multi-hop swaps), that residual input token/ETH is left sitting in the `LifiExternalAction` contract balance. Unlike `Hinkal.sol`'s own accounting — which strictly enforces `balanceDif == amountChanges[i] + utxoAmount` for tokens moved directly by `Hinkal` [4](#0-3)  — this equality is only checked against `Hinkal`'s own balance change, not against what actually happened inside the external-action contract. There is no code in `ExternalActionBaseV2`, `ExternalActionSwap`, or `LifiExternalAction` that sweeps or refunds leftover input-token balance back to the user or to `Hinkal`: [5](#0-4) 

This breaks the equality "value pulled from the vault for a swap == value the router consumed + value returned to the user"; the delta is silently stranded.

### Impact Explanation
Any leftover input-token amount from an under-filled LI.FI swap is permanently locked in the `LifiExternalAction` contract with no owner/withdraw or refund mechanism reachable to return it to the depositing user, resulting in permanent freezing (loss) of user funds equal to the residual amount. This matches the High-impact category "permanent freezing of user funds."

### Likelihood Explanation
Likelihood depends on how often LI.FI routes leave dust/unspent input relative to the amount pulled from Hinkal — this can occur under normal (non-malicious) aggregator behavior such as partial fills, slippage-driven route adjustments, or cross-chain bridge calls that refund excess natively to the caller contract rather than consuming it fully. Because `externalActionMetadata`/router call data is supplied at transaction time and not strictly bound to guarantee full consumption of `inputAmount`, this is a realistic operational scenario rather than a purely theoretical one, though it requires the router's actual behavior (external, LI.FI-controlled) to leave a nonzero residual.

### Recommendation
In `ExternalActionSwap.swap()` (or `LifiExternalAction.callRouter`), measure the input token balance before and after the router call, and if any residual remains, either revert the swap or immediately return the leftover input token to `msg.sender` (i.e., back to the `Hinkal` vault via `transferERC20TokenOrETH`) so it can be re-credited to the user's shielded balance, analogous to the recommended fix in the referenced wfCash report.

### Proof of Concept
1. User initiates a Hinkal external-action swap through `LifiExternalAction`, pulling `inputAmount` of token A out of the Hinkal vault into the `LifiExternalAction` contract via `_externalTransact`.
2. The supplied `externalActionMetadata` executes a LI.FI route that, due to routing/partial-fill behavior, only consumes `inputAmount - X` of token A, leaving `X` of token A (or native ETH) sitting in the `LifiExternalAction` contract balance.
3. `callRouter` computes `swappedAmount` purely from the output token B balance delta; the unspent `X` of token A is never measured or forwarded anywhere.
4. `swap()` forwards only `swappedAmount` of token B back to Hinkal; the `X` of token A remains stuck in `LifiExternalAction` forever, since neither `ExternalActionBaseV2` nor `LifiExternalAction` expose any sweep/refund function reachable by the user or Hinkal.

### Citations

**File:** contracts/Hinkal.sol (L134-146)
```text
                // balance equation to check: CHANGE IN BALANCE SHOULD EQUAL TO
                // 1) change in off-chain utxos
                // 2) change in on-chain utxos
                require(
                    balanceDif ==
                        (
                            circomData.onChainCreation[i]
                                ? int256(0)
                                : circomData.amountChanges[i]
                        ) +
                            int256(utxoAmount),
                    "Balance Diff Should be equal to sum of onchain and offchain created commitments"
                );
```

**File:** contracts/Hinkal.sol (L244-256)
```text
        int256[] memory deltaAmountChanges = new int256[](
            circomData.erc20TokenAddresses.length
        );
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            deltaAmountChanges[i] = _calculateDeltaAmount(circomData, i);
            if (deltaAmountChanges[i] < 0) {
                transferERC20TokenOrETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    uint256(-deltaAmountChanges[i])
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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L63-102)
```text
        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );

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
