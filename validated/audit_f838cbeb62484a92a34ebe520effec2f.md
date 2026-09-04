## Analysis

This repo's `ExternalActionSwap.sol` (used for LI.FI-routed swaps) reproduces the exact bug class from the M-05 report: an amount debited from the user's shielded balance based on the *requested* input, while the actual amount consumed by the external swap can be smaller, with no refund mechanism for the difference.

### Title
Leftover swap input token is neither refunded nor accounted for, permanently trapping user funds - (File: contracts/external-actions/swaps/ExternalActionSwap.sol)

### Summary
`ExternalActionSwap.swap()` computes `inputAmount` from the circuit-committed `deltaAmounts[0]` (the full amount the ZK proof says was withdrawn from the user's shielded balance) and forwards it to `callRouter`. If the underlying router call (LI.FI, which can wrap DEX pools using partial-fill / limit-price semantics analogous to the Maverick `Router.sol` bug) consumes less than the full `inputAmount`, the unspent `inputToken` remains on the `ExternalActionSwap`/`LifiExternalAction` contract balance. The function only ever computes and forwards the `outputToken` delta (`swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore`); it never checks or returns leftover `inputToken` balance to the caller.

### Finding Description
In `_externalTransact` (`contracts/Hinkal.sol:244-256`), Hinkal transfers the full negative `deltaAmountChanges[i]` (i.e., the entire committed input amount) out of Hinkal into the external action contract *before* `runAction` executes: [1](#0-0) 

`ExternalActionSwap.swap()` then takes that full `inputAmount` and calls the router: [2](#0-1) 

`LifiExternalAction.callRouter` executes an arbitrary router call with the input amount and measures `swappedAmount` purely from the `outputToken` balance delta, never checking whether all of `inputAmount` of `inputToken` was actually consumed: [3](#0-2) 

Back in `swap()`, only `outputToken` is ever transferred back to Hinkal (`msg.sender`) as a UTXO; there is no branch that checks for or returns unspent `inputToken`: [4](#0-3) 

This breaks the protocol's balance equality: the circuit's public inputs (via `circomData.amountChanges` / `deltaAmounts`) commit that the *entire* `inputAmount` left the user's shielded balance and was converted into `outputToken`, and Hinkal enforces this via the slippage/balance check in `_externalTransact`'s caller (`Hinkal.sol` balance-diff `require`). But when the router only partially consumes `inputToken` (a normal, permitted DEX/aggregator behavior — e.g., partial fill, limit price, or leftover dust from multi-hop routing), the unspent `inputToken` is stranded on the `ExternalActionSwap`/`LifiExternalAction` contract. `ExternalActionBaseV2` and `ExternalActionSwap` expose no sweep/rescue function for this balance: [5](#0-4) 

so the value is not returned to the user, is not represented as a UTXO in the shielded pool, and (absent an owner-only sweep, which is out of scope to rely on) is either permanently stuck or up-for-grabs by anyone able to reach the router's leftover-refund path (e.g., an aggregator that refunds leftover input to `msg.sender`, which here is the `ExternalActionSwap` contract itself, not the user).

### Impact Explanation
This is a **temporary/permanent freezing of user funds**: the shielded balance accounting treats the full `inputAmount` as spent (it is deducted from the user's Hinkal nullifiers), while the real, on-chain unspent portion of `inputToken` is left in the external-action contract with no code path to return it to the user or credit it back into the shielded pool.

### Likelihood Explanation
This is triggered any time a LI.FI-routed swap (or any DEX route it aggregates) doesn't fully consume the requested input — a routine occurrence for limit-price-protected or partial-fill-capable pools, not an edge case requiring privileged access. No admin, relayer, or attacker cooperation is needed; it happens automatically during normal proof-authorized swap execution.

### Recommendation
After `callRouter` returns, measure the actual `inputToken` balance change as well as the `outputToken` change. If `inputToken` balance in the external action contract increased (i.e., leftover unspent input), either revert the transaction, or fold the leftover into an additional UTXO returned to Hinkal so it is credited back to the user's shielded balance instead of being stranded in the external action contract.

### Proof of Concept
1. User submits a swap proof via `Hinkal.transact` with `externalActionData.externalActionId` pointing at `LifiExternalAction`, requesting a swap of `inputAmount` of `inputToken` for `outputToken`, with `circomData.amountChanges` committing the full `inputAmount` as spent.
2. `Hinkal._externalTransact` transfers the full `inputAmount` of `inputToken` to `LifiExternalAction`.
3. `LifiExternalAction.callRouter` forwards `externalActionMetadata` to the LI.FI router, which internally routes through a DEX pool that only partially fills the trade (e.g., due to a limit-price/slippage-protection mechanism analogous to the M-05 Maverick bug), consuming only a fraction of `inputAmount`.
4. `swappedAmount` is computed solely from the `outputToken` balance delta; the leftover `inputToken` balance remains on `LifiExternalAction`.
5. `swap()` transfers only `outputToken` back to Hinkal and creates a UTXO only for `outputToken`; the leftover `inputToken` is never returned, never becomes a UTXO, and there is no sweep function to recover it — it is stuck, breaking the balance equality between what was debited from the user's shielded balance and what was actually delivered/returned.

### Citations

**File:** contracts/Hinkal.sol (L244-261)
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

        return
            IExternalActionV2(circomData.externalActionData.externalAddress)
                .runAction(circomData, deltaAmountChanges);
    }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L40-68)
```text
    function swap(
        CircomData calldata circomData,
        int256[] calldata deltaAmounts
    ) internal returns (UTXO[] memory utxoSet) {
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

        require(
            block.timestamp <= circomData.timeStamp + SWAP_DEADLINE_WINDOW,
            "swap expired"
        );

        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L89-102)
```text
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
