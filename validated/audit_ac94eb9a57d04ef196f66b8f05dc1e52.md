### Title
`hinkalFee` (protocol fee) is stranded permanently in `ExternalActionSwap` when `relay == address(0)` - ([File: contracts/external-actions/swaps/ExternalActionSwap.sol])

### Summary
In `ExternalActionSwap.swap`, the variable-rate `hinkalFee` is unconditionally subtracted from `amountToSendToHinkal` (the amount forwarded back to `Hinkal.sol`/the user's new UTXO), but it is only actually paid out via `sendToRelay`, which is a silent no-op when `circomData.relay == address(0)`. Since `relay == address(0)` is an explicitly valid, unprivileged path (enforced by `performHinkalChecks`'s `originalSender`/`relay` check in `contracts/HinkalHelper.sol`), any user doing a self-relayed swap causes `hinkalFee` to be permanently deducted from what the user receives yet never delivered anywhere, leaving it stuck as the action contract's own token balance.

### Finding Description
The broken equality: tokens leaving the swap action contract must equal `swappedAmount` (what the router returned) — i.e. `amountToSendToHinkal + amountActuallySentToRelay == swappedAmount`. The code instead computes: [1](#0-0) 

`hinkalFee = hinkalHelper.calculateRelayFee(swappedAmount, 0, feeStructure.variableRate)` is computed unconditionally, and `totalFee` (which includes `hinkalFee`) is subtracted from `swappedAmount` to get `amountToSendToHinkal`, regardless of whether `sendToRelay` actually transferred anything. `sendToRelay` itself is a no-op when `relay == address(0)`: [2](#0-1) 

So when `relay == address(0)`:
- `amountToSendToHinkal = swappedAmount - hinkalFee (- relayFee if same token)` is sent to `msg.sender` (Hinkal.sol, crediting the user's UTXO for less than the true swap output).
- `sendToRelay(address(0), hinkalFee, outputToken)` silently does nothing.
- The `hinkalFee` (and `relayFee` if in a different token from `outputToken`) remains as `outputToken` balance sitting in the `LifiExternalAction`/`ExternalActionSwap` contract, uncredited to anyone.

This is reachable directly by an unprivileged EOA: `performHinkalChecks` in `contracts/HinkalHelper.sol` explicitly permits and requires `relay == address(0)` when `originalSender == sender` (self-relay, i.e., the user calls Hinkal directly without a relay) — this is a supported, legitimate flow, not a bypass: [3](#0-2) 

`_internalTransact` in `Hinkal.sol` correctly guards this for its own fee routing (`relayFee = 0` when `circomData.relay == address(0)`, and the full amount is returned to the recipient): [4](#0-3) 

But `ExternalActionSwap.swap` has no equivalent conditional — `hinkalFee` is always carved out of the user's `amountToSendToHinkal` whether or not a relay exists to receive it. There is no sweep, admin-withdraw, or fee-harvest function in `ExternalActionSwap.sol` to recover this balance; it can only be absorbed accidentally into a future, unrelated caller's `swappedAmount` calculation is actually incorrect too — since `swappedAmount = balanceAfter - balanceBefore` in `LifiExternalAction.callRouter`, the stranded residual is already counted in `balanceBefore` for all subsequent calls and is never re-extracted; it simply accumulates in the contract forever.

### Impact Explanation
Protocol fee revenue (`hinkalFee`, computed via `feeStructure.variableRate`) is permanently frozen inside the `ExternalActionSwap`/`LifiExternalAction` contract on every self-relayed (`relay == address(0)`) swap with nonzero `variableRate`. This matches the High-severity category "theft or permanent freezing of protocol/relay fees." It is fully repeatable — any unprivileged user performing a normal swap via the supported self-relay path triggers it every time, with no attacker cost beyond a normal swap fee, and the frozen amount only grows over time with no recovery mechanism in the contract.

### Likelihood Explanation
No special preconditions are required beyond: (1) a working swap route through `LifiExternalAction`, (2) `circomData.relay == address(0)` (a fully legitimate, unprivileged, protocol-supported value per `HinkalHelper.performHinkalChecks`), and (3) `feeStructure.variableRate > 0` (a normal, expected value set by the fee structure for protocol revenue). This requires no proof-bypass, no privileged role, and no unusual token/route setup — it occurs on ordinary usage of the self-relay swap feature.

### Recommendation
In `ExternalActionSwap.swap`, only deduct `hinkalFee` (and `relayFee`) from `amountToSendToHinkal` when `circomData.relay != address(0)` (mirroring the pattern in `Hinkal.sol::_internalTransact`), e.g. compute `hinkalFee = 0` and `relayFee = 0` when `relay == address(0)` before calling `sendToRelay`, so the full `swappedAmount` is credited back to the user's UTXO instead of being silently withheld and stranded.

### Proof of Concept
Hardhat test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `LifiExternalAction` (or a mock router matching `callRouter`'s interface) with a mock ERC20 output token.
2. Register the swap action in `Hinkal.externalActionMap`.
3. Craft a valid proof/`CircomData` for a self-relay swap: `circomData.relay = address(0)`, `circomData.originalSender = msg.sender`, `feeStructure.variableRate = 500` (5%), `feeStructure.flatFee = 0`, input/output tokens distinct.
4. Execute the swap through `Hinkal` (or directly call `LifiExternalAction.runAction`/`swap` if testing at the action level with `onlyAllowedRecipient` set appropriately).
5. Assert: `outputToken.balanceOf(LifiExternalAction address)` after the call equals the computed `hinkalFee` (nonzero) — i.e., `balanceOf(action) == calculateRelayFee(swappedAmount, 0, variableRate)`.
6. Assert the user's minted UTXO amount (`amountToSendToHinkal`) is strictly less than `swappedAmount` by exactly `hinkalFee`, and that no relay or fee recipient balance increased by that amount in the same transaction — confirming the fee is neither delivered nor recoverable in that transaction.

### Citations

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L70-93)
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

**File:** contracts/Hinkal.sol (L188-223)
```text
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
```
