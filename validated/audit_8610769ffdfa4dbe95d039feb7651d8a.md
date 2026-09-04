### Title
LI.FI swap external action leaks any non‑`outputToken` proceeds returned by the aggregator, permanently freezing user value - (File: `contracts/external-actions/swaps/LifiExternalAction.sol`, `contracts/external-actions/swaps/ExternalActionSwap.sol`)

### Summary
`LifiExternalAction.callRouter()` only measures the balance delta of the declared `outputToken` before/after the raw `router.call(externalActionMetadata)`, and `ExternalActionSwap.swap()` only ever moves/accounts for `erc20TokenAddresses[0]` (input) and `erc20TokenAddresses[1]` (output). Just like the 0x `transformERC20` report, LI.FI routes can legitimately return other tokens to the caller (positive-slippage refunds, fee-token rebates, leftover intermediate-hop tokens, etc.). Because the swap contract itself is the direct caller of the router (not the Hinkal core), any such “extra” token lands on `LifiExternalAction`/`ExternalActionSwap`'s own balance and is never transferred out, never wrapped into a UTXO, and never reflected in Hinkal's outer balance-diff equation (which only iterates `circomData.erc20TokenAddresses`, i.e. the two declared tokens).

### Finding Description
`ExternalActionSwap.swap()` calls `callRouter(inputToken, inputAmount, outputToken, ...)`: [1](#0-0) 

`LifiExternalAction.callRouter()` executes the arbitrary LI.FI calldata (`externalActionMetadata`) directly from the swap contract's own address, and computes `swappedAmount` solely from the `outputToken` balance delta: [2](#0-1) 

Only `swappedAmount` of `outputToken` is ever forwarded to `msg.sender` (`transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal)`), and only one `UTXO` for `outputToken` is produced: [3](#0-2) 

Hinkal's outer accounting in `_externalTransact`/`transact` only checks balance differences for the tokens listed in `circomData.erc20TokenAddresses` (i.e., the declared input/output pair), so a third token accrued to the swap contract is invisible to the balance equation entirely: [4](#0-3) 

Neither `ExternalActionSwap` nor its base (`ExternalActionBaseV2`, which only exposes `setAllowedRecipients`/`runAction`) contains any rescue/sweep/withdraw function for arbitrary ERC-20 balances: [5](#0-4) 

Since `externalActionMetadata` is attacker/relayer-supplied calldata forwarded verbatim to the LI.FI `router`, any LI.FI route (chosen by the user/relayer through the front end or crafted directly) that causes the router to send back a token other than the declared `outputToken` — e.g. a route with positive slippage refunded in the sell token, a fee rebate, or a multi-hop leftover — results in that token being stranded permanently in the `LifiExternalAction` contract with no code path to recover or credit it to any user's shielded balance.

### Impact Explanation
This breaks the core balance equation Hinkal relies on: value that is moved into the protocol's external-action contract by an external call is not counted by `circomData.amountChanges`/`slippageValues`/UTXO creation, and there is no sweep mechanism, so the value is permanently frozen and effectively lost to the depositing user (and to Hinkal, since it can't be attributed to any shielded UTXO or relay fee). This matches the "permanent freezing of user funds" high/critical impact category.

### Likelihood Explanation
Likelihood is realistic given normal aggregator behavior: LI.FI/0x-style routers commonly refund positive slippage or leftover dust in a token different from the nominal `outputToken`, and `externalActionMetadata` is fully attacker/relayer-controlled calldata forwarded to `router.call`, so a user (or a relayer building the route) can trivially select or be assigned such a route without any additional privilege.

### Recommendation
Do not rely solely on the declared `outputToken` balance delta. Either (a) restrict `externalActionMetadata` to a whitelisted, decoded set of LI.FI facets/selectors and validate that all tokens moved by the route are enumerable and accounted for, or (b) generalize the accounting in `ExternalActionSwap.swap()`/`Hinkal.sol` to snapshot balances of every token that could plausibly be touched by the route and fold any residual increase back into the UTXO output set (or add an owner/permissionless sweep that credits stray balances into a new shielded UTXO for the depositor), so no value can silently accrue to the contract outside the balance equation.

### Proof of Concept
1. A user submits a swap through `LifiExternalAction` with `inputToken = TOKEN_A`, `outputToken = TOKEN_B`, and `externalActionMetadata` encoding a LI.FI route through a DEX aggregator step that is known (or can be crafted) to refund positive slippage in `TOKEN_A` (or a third `TOKEN_C`) directly to `msg.sender` of the router call, which is `LifiExternalAction`'s own address (see `router.call(externalActionMetadata)` in `contracts/external-actions/swaps/LifiExternalAction.sol:31`).
2. `callRouter` measures only `getERC20OrETHBalance(outputToken)` before/after; the `TOKEN_A`/`TOKEN_C` refund is not part of this delta.
3. `swap()` transfers only `swappedAmount` of `outputToken` back to Hinkal and creates a single UTXO for `outputToken`; the refunded `TOKEN_A`/`TOKEN_C` remains on `LifiExternalAction`'s balance.
4. Hinkal's `_externalTransact`/balance-diff loop in `contracts/Hinkal.sol:88-146` only iterates over `circomData.erc20TokenAddresses` (the declared input/output pair), so it never observes or accounts for the stranded token.
5. Because `ExternalActionBaseV2`/`ExternalActionSwap` expose no sweep/withdraw function for arbitrary ERC-20 balances, the refunded tokens are permanently unrecoverable by the depositing user, constituting a permanent freeze of that portion of user funds.

### Citations

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L63-101)
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

**File:** contracts/Hinkal.sol (L88-146)
```text
            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            OnChainCommitment[]
                memory onChainCommitments = new OnChainCommitment[](
                    utxoSet.length
                );
            uint256 onChainCommitmentCounter = 0;
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
