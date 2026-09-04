### Title
Third-token refunds from `router.call()` become permanently stranded in `LifiExternalAction` - (File: `contracts/external-actions/swaps/LifiExternalAction.sol`)

### Summary
`LifiExternalAction.callRouter()` only measures the balance delta of `outputToken` before/after the raw `router.call(externalActionMetadata)`, and `Hinkal.transact()` only reconciles balances for `circomData.erc20TokenAddresses` (input/output tokens declared by the prover). Any token received by `LifiExternalAction` from the router that is neither `inputToken` nor `outputToken` is invisible to both accounting layers and has no sweep path, so it is permanently trapped in the contract.

### Finding Description
The broken equality is: **tokens entering `LifiExternalAction` from the router == sum of `amountChanges`/UTXOs credited back to the user**. This is enforced only for the two tokens listed in `circomData.erc20TokenAddresses` — `inputToken = circomData.erc20TokenAddresses[0]` and `outputToken = circomData.erc20TokenAddresses[1]` [1](#0-0) .

`callRouter` computes `swappedAmount` strictly from the `outputToken` balance delta around the low-level call: [2](#0-1) 

If the crafted `externalActionMetadata` causes the LI.FI router to send a refund (unswapped dust, slippage remainder, bridge fee refund, etc.) in a third token `C` to `address(this)` (i.e., `LifiExternalAction`), that increase in `C`'s balance is never read, never included in `swappedAmount`, never transferred out via `transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal)` [3](#0-2) , and never represented in the returned `utxoSet` (which only contains `outputToken`) [4](#0-3) .

At the `Hinkal.transact()` level, the balance-diff/slippage/UTXO-sum equality is checked per-token only over `circomData.erc20TokenAddresses` [5](#0-4) , and that check is performed against `Hinkal`'s own balances, not `LifiExternalAction`'s. Since token `C` is not in `erc20TokenAddresses`, it is structurally excluded from any check in this call. `ExternalActionBaseV2` and `Transferer` expose no rescue/sweep function reachable by a non-owner to recover it [6](#0-5) .

Call sequence: `Hinkal.transact` → `_externalTransact` → `IExternalActionV2(LifiExternalAction).runAction` → `ExternalActionSwap.swap` → `LifiExternalAction.callRouter` → `router.call(externalActionMetadata)` refunds token `C` to `address(this)`. No guard in `performHinkalChecks`, `verifyProof`, or the circuit's `inTotal + amountChanges === outTotal` constraint can catch this because the circuit and on-chain checks are both parameterized by the prover-supplied `erc20TokenAddresses` list, which the attacker deliberately keeps at length 2 (input/output only).

### Impact Explanation
Any ERC-20 value sent by the LI.FI router to `LifiExternalAction` outside of `inputToken`/`outputToken` is permanently frozen inside the contract with no accounting path or sweep mechanism reachable by an unprivileged user — this is a permanent freezing of value that entered the protocol's external-action contract, matching the Critical "permanent freezing of user funds" category. The stuck balance also is not later "drained" by other swaps that pick `outputToken == C`, because `callRouter`'s `balanceBefore` snapshot already includes the stranded balance, so `swappedAmount = balanceAfter - balanceBefore` for the new user correctly excludes it — it simply stays inert forever rather than being stolen by a subsequent depositor.

### Likelihood Explanation
The precondition is that the LI.FI router (or any router reachable behind this `router` address) actually executes a call path that returns a token other than the declared input/output token to the caller — a legitimate behavior for aggregators handling multi-hop bridging, partial-fill dust, or fee-token refunds. The attacker fully controls `externalActionMetadata` (opaque calldata forwarded verbatim to `router.call`), controls their own deposit and swap parameters, and needs no privileged role. Whether this is triggerable depends on the concrete router's supported instruction set, which is external to this repo and not verifiable purely from the Hinkal/circuits code.

### Recommendation
Do not rely solely on `outputToken`-only balance deltas in `callRouter`/`swap`. After the router call, sweep or account for any non-zero balance changes on tokens other than `inputToken`/`outputToken` (e.g., forward excess balances of arbitrary tokens back to `msg.sender`/the depositor, or restrict router calldata to a strict allow-list of selectors/tokens verified against `erc20TokenAddresses`), and/or add an owner-independent, per-user-claimable sweep tied to the UTXO/stealth address so unexpected refund tokens are not permanently unclaimable.

### Proof of Concept
Deploy a mock LI.FI router whose fallback, upon `router.call(metadata)`, performs the expected `outputToken` transfer to `LifiExternalAction` but also transfers a fixed amount of an unrelated ERC-20 `TokenC` to `address(this)` (the caller, i.e., `LifiExternalAction`). Drive a full `Hinkal.transact` call with a locally generated proof where `circomData.erc20TokenAddresses = [inputToken, outputToken]` (no `TokenC`), and:
- Before: assert `TokenC.balanceOf(LifiExternalAction) == 0`.
- After the transaction succeeds: assert `TokenC.balanceOf(LifiExternalAction) > 0`.
- Assert no `UTXO`/commitment exists for `TokenC` in `outCommitments`/`onChainCommitments`, and that no subsequent transaction (including one with `erc20TokenAddresses[1] == TokenC`) increases any user's claimable balance by that stranded amount, confirming it is permanently unclaimable.

### Citations

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L44-56)
```text
        address inputToken = circomData.erc20TokenAddresses[0];
        uint256 inputAmount = uint256(-deltaAmounts[0]);

        if (inputToken == circomData.feeStructure.feeToken) {
            inputAmount -= circomData.feeStructure.flatFee;
        }

        address outputToken = circomData.erc20TokenAddresses[1];

        require(
            circomData.slippageValues[1] != 0,
            "swap output slippage floor not set"
        );
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L91-93)
```text
        uint256 amountToSendToHinkal = swappedAmount - totalFee;

        transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L95-102)
```text
        utxoSet = new UTXO[](1);
        utxoSet[0] = UTXO({
            amount: amountToSendToHinkal,
            erc20Address: outputToken,
            stealthAddressStructure: circomData.stealthAddressStructure,
            timeStamp: block.timestamp
        });
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

**File:** contracts/Hinkal.sol (L97-146)
```text
            for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {
                int256 balanceDif;

                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
                } else {
                    balanceDif =
                        int256(newBalances[i]) -
                        int256(oldBalances[i]);
                }
                // balance inequality to check that minimum amount of token is received/given
                require(
                    balanceDif >= circomData.slippageValues[i],
                    "slippage param is violated"
                );

                uint256 utxoAmount = 0;
                for (uint j = 0; j < utxoSet.length; j++) {
                    if (
                        utxoSet[j].erc20Address ==
                        circomData.erc20TokenAddresses[i]
                    ) {
                        utxoAmount += utxoSet[j].amount;

                        onChainCommitments[
                            onChainCommitmentCounter
                        ] = createOnchainCommitment(
                            utxoSet[j],
                            circomData.onChainEncryptedOutput
                        );
                        onChainCommitmentCounter++;
                    }
                }

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

**File:** contracts/external-actions/ExternalActionBaseV2.sol (L1-42)
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
```
