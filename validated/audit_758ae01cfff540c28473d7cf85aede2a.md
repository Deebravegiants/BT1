### Title
Protocol/relay fee permanently frozen in `ExternalActionSwap` when `relay == address(0)` - ([File: contracts/external-actions/swaps/ExternalActionSwap.sol])

### Summary
`ExternalActionSwap.swap()` always deducts `hinkalFee` (and `relayFee`) from the swap output before sending the remainder to `msg.sender`, but the actual transfer of that fee is delegated to `Transferer.sendToRelay`, which is a no-op whenever `relay == address(0)`. Because `HinkalHelper.performHinkalChecks` explicitly permits `circomData.relay == address(0)` (self-relayed transactions where `originalSender == sender`), and nothing on-chain forces `feeStructure.variableRate`/`flatFee` to be zero in that mode, an attacker can submit a self-relayed swap with a nonzero `variableRate`, causing `hinkalFee` tokens to be silently stranded inside the `ExternalActionSwap` contract with no recovery path.

### Finding Description
The equality that should hold is: `amount debited from swap output as fee` == `amount actually delivered to a fee recipient (relay or protocol)`.

Trace:
- `HinkalHelper.performHinkalChecks` allows `relay == address(0)` as long as `circomData.originalSender == sender` (self-relay path): [1](#0-0) 
- It only bounds `variableRate <= 10000`; it never forces `variableRate == 0` (or `flatFee == 0`) when `relay == address(0)`: [2](#0-1) 
- In `ExternalActionSwap.swap`, `hinkalFee` is computed unconditionally from `swappedAmount` and `circomData.feeStructure.variableRate`, independent of whether `relay` is set: [3](#0-2) 
- The fee is "sent" via `sendToRelay(circomData.relay, ..., outputToken)`, but `Transferer.sendToRelay` only transfers when `relay != address(0)`; otherwise it does nothing: [4](#0-3) 
- Regardless of that no-op, `totalFee` is still subtracted from `swappedAmount` before computing what is sent to `msg.sender` (Hinkal contract, on behalf of the shielded pool/user): [5](#0-4) 

So when `relay == address(0)`: the tokens/ETH equal to `relayFee + hinkalFee` are neither sent to a relay (no-op) nor included in `amountToSendToHinkal` (subtracted out) nor sent to the zero address (burned) — they simply remain in the `ExternalActionSwap` contract's balance. There is no sweep/withdraw function anywhere in this contract, `ExternalActionBaseV2`, or `OwnerHinkal` (which only extends `Ownable2Step` with a blocked `renounceOwnership`): [6](#0-5) [7](#0-6) . This makes the stranded fee permanently unrecoverable by anyone, including the owner.

Attacker call: submit `transact()` with `circomData.externalActionData.externalActionId` pointing at the swap action, `circomData.relay = address(0)`, `circomData.originalSender = msg.sender`, and `circomData.feeStructure.variableRate > 0` (and/or `flatFee > 0`). The swap executes normally, `hinkalFee`/`relayFee` is computed and silently dropped inside the external action contract.

Existing guards that fail to prevent this:
- `performHinkalChecks` validates the relay/originalSender relationship but not the fee schedule against relay presence.
- `dimensionsCheck` and `checkOnchainCreation` don't reference `feeStructure` fields relevant here.
- The outer `Hinkal._internalTransact` guard `require(circomData.relay == address(0) || hasPaidToRelay, "relay not paid")` only applies to the internal-transact path, not to `_externalTransact` → `ExternalActionSwap.swap`, so it provides no protection here.

### Impact Explanation
Tokens/ETH equal to `hinkalFee` (and `flatFee` when applicable) are permanently locked inside the `ExternalActionSwap` contract on every self-relayed swap with nonzero `variableRate`/`flatFee`. This is a protocol-fee freezing bug: value that the fee schedule committed to (and that was deducted from the user's swap output) never reaches its intended recipient and cannot be recovered by anyone. This is repeatable on every self-relayed swap transaction and can be triggered deliberately by any unprivileged user who controls `circomData.relay`, `circomData.feeStructure`, matching the "High - permanent freezing of protocol/relay fees" category.

### Likelihood Explanation
Preconditions are trivial and fully attacker-controlled: set `relay = address(0)` and `originalSender = msg.sender` (both explicitly allowed by `performHinkalChecks`), and set a nonzero `variableRate` in `feeStructure` (bounded only by `<= 10000`). No special tree state, no privileged role, no collusion needed — a single swap transaction with a self-generated proof suffices. It is fully repeatable and costs nothing extra beyond the fee amount itself (which the attacker/user was already paying regardless of relay presence, so there's no economic disincentive to trigger the freeze — it happens by default unless callers are careful to zero the fee fields for self-relay).

### Recommendation
Enforce that when `circomData.relay == address(0)`, `feeStructure.variableRate` and `feeStructure.flatFee` must be zero (add this check in `HinkalHelper.performHinkalChecks` or `dimensionsCheck`), so no fee is ever computed/deducted in the self-relay path. Alternatively/additionally, change `ExternalActionSwap.swap` to skip fee computation entirely and forward the full `swappedAmount` to `msg.sender` when `circomData.relay == address(0)`, mirroring the internal-transact behavior where relay fee logic is gated behind `circomData.relay != address(0)`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, and a `ExternalActionSwap`-derived contract (e.g., a test router mock returning a fixed `swappedAmount`).
2. Register the swap external action in `Hinkal`.
3. Build valid `CircomData` for a self-relayed swap: `relay = address(0)`, `originalSender = attacker`, `feeStructure.variableRate = 500` (5%), `feeStructure.flatFee = 0`, output token = some ERC20.
4. Generate a valid proof for these public inputs (locally, using project's circuit/proving setup) satisfying `performHinkalChecks`/`verifyProof`.
5. Call `Hinkal.transact(...)` as attacker.
6. Assert:
   - `outputToken.balanceOf(attacker's resulting shielded UTXO / Hinkal contract)` == `swappedAmount - hinkalFee` (fee was deducted from user).
   - `outputToken.balanceOf(relay)` == 0 (relay is zero address, nothing received).
   - `outputToken.balanceOf(ExternalActionSwap contract)` == `hinkalFee` (fee stuck in contract).
   - No function exists on `ExternalActionSwap`/`OwnerHinkal` callable by the owner to withdraw this stranded balance — confirm by attempting `vm.expectRevert` on any guessed withdraw call, or by absence of such a selector in the ABI.

### Citations

**File:** contracts/HinkalHelper.sol (L167-171)
```text
        require(
            circomData.feeStructure.variableRate <= 10000,
            "Variable rate cannot be greater than 10000"
        );
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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L70-76)
```text
        uint256 relayFee = circomData.feeStructure.flatFee;

        uint256 hinkalFee = hinkalHelper.calculateRelayFee(
            swappedAmount,
            0,
            circomData.feeStructure.variableRate
        );
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L89-93)
```text
        uint256 totalFee = hinkalFee +
            (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
        uint256 amountToSendToHinkal = swappedAmount - totalFee;

        transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);
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

**File:** contracts/OwnerHinkal.sol (L1-10)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable2Step.sol";

contract OwnerHinkal is Ownable2Step {
    function renounceOwnership() public view override onlyOwner {
        revert("The Ownership cannot be renounced");
    }
}
```

**File:** contracts/external-actions/ExternalActionBaseV2.sol (L9-43)
```text
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
