### Title
Fee is deducted from swap output even with `relay == address(0)`, permanently stranding relay/protocol fees in `ExternalActionSwap` - (File: contracts/external-actions/swaps/ExternalActionSwap.sol)

### Summary
`ExternalActionSwap.swap` always computes `hinkalFee`/`relayFee` from `circomData.feeStructure` and subtracts `totalFee` from `swappedAmount` before crediting the user's UTXO, but the actual transfer of that fee via `sendToRelay` is a no-op whenever `circomData.relay == address(0)`. This lets any unprivileged user submit a self-relayed swap (`relay == address(0)`, `originalSender == msg.sender`, which `performHinkalChecks` explicitly allows) with a non-zero `feeStructure.variableRate`/`flatFee`, causing the fee value to be silently trapped in the `ExternalActionSwap`/`LifiExternalAction` contract with no rescue mechanism, while the user's shielded output UTXO is reduced by that exact amount.

### Finding Description
The broken equality: `totalFee` (value removed from `amountToSendToHinkal`, and thus from the user's shielded output) must equal the value actually delivered to a relay/fee recipient via `sendToRelay`. In `ExternalActionSwap.swap`: [1](#0-0) 

`relayFee`/`hinkalFee` are computed unconditionally from `circomData.feeStructure`, and `sendToRelay(circomData.relay, ...)` is called with whatever `circomData.relay` is. `sendToRelay` itself is a no-op transfer when `relay == address(0)`: [2](#0-1) 

Meanwhile `amountToSendToHinkal = swappedAmount - totalFee` is computed independently of whether the transfer succeeded, so the fee amount is deducted from the user's output UTXO regardless. Because `circomData.relay == address(0)` never reverts the transfer, the fee tokens remain sitting in the `ExternalActionSwap`/`LifiExternalAction` contract's own balance — not delivered to any relay, not returned to the user, and there is no owner/rescue function to retrieve stray ERC20/ETH balances (`OwnerHinkal` only overrides `renounceOwnership`).

`HinkalHelper.relayerIsValid` only enforces `tx.origin == relay` and whitelist membership when `relay != address(0)`, so it does not prevent `relay == address(0)`: [3](#0-2) 

And `performHinkalChecks` explicitly *permits* `relay == address(0)` as a valid, self-submitted transaction mode (requiring `originalSender == sender`): [4](#0-3) 

`dimensionsCheck` only bounds `feeStructure.variableRate <= 10000` and never ties fee presence to `relay != 0`: [5](#0-4) 

Notably, the codebase's own internal-transfer path (`Hinkal._internalTransact`) demonstrates the correct invariant: it only computes and deducts `relayFee` **inside** the `if (circomData.relay != address(0))` branch, and explicitly requires `circomData.relay == address(0) || hasPaidToRelay`, guaranteeing that when there is no relay, no fee is deducted from the recipient at all: [6](#0-5) 

`ExternalActionSwap.swap` does not replicate this guard — it computes and subtracts the fee unconditionally, independent of `circomData.relay`.

Attacker's exact call: an unprivileged EOA deposits funds, then calls `Hinkal.transact` with `circomData.relay == address(0)`, `circomData.originalSender == msg.sender`, `externalActionData.externalActionId` pointing at a registered `LifiExternalAction`, and a `feeStructure` with non-zero `variableRate`/`flatFee` baked into a valid proof for their own swap. The swap executes, `sendToRelay` silently drops the fee transfer, and the user's resulting UTXO is `swappedAmount - totalFee` instead of `swappedAmount` — the difference is stuck as an unaccounted token balance in the external-action contract.

### Impact Explanation
This does not steal user funds beyond what the user's own proof already commits to lose (the user chooses the fee values baked into their own proof), and no relay is defrauded since no whitelisted relay is owed anything for a self-submitted transaction. The realizable harm is that `totalFee` worth of tokens becomes permanently stuck in the `ExternalActionSwap`/`LifiExternalAction` contract balance with no recovery path — value that was implicitly meant to go to a relay/protocol never reaches anyone and is unrecoverable. This matches the "High - permanent freezing of protocol/relay fees" category, since the fee amount is neither delivered to a relay nor returned to the user, and is trapped indefinitely in contract storage. It is repeatable per self-relayed swap transaction with `variableRate`/`flatFee` > 0.

### Likelihood Explanation
Preconditions are trivially met by any unprivileged user: deposit funds normally, generate a valid proof for a swap through `LifiExternalAction` with `relay = address(0)` and `originalSender = msg.sender` (an explicitly allowed, checked path), and set any non-zero `feeStructure.flatFee`/`variableRate` in that proof. No relay, admin, or privileged role is required. The attacker cost is just their own reduced output (they are the one losing the fee amount into limbo), so the primary incentive is not attacker profit but protocol fund loss/breakage; still, it is fully attacker-triggerable and repeatable at will, and it is a real defect regardless of whether the "attacker" benefits directly.

### Recommendation
In `ExternalActionSwap.swap`, mirror the guard used in `Hinkal._internalTransact`: only compute and deduct `hinkalFee`/`relayFee` when `circomData.relay != address(0)`; when `circomData.relay == address(0)`, set `totalFee = 0` so `amountToSendToHinkal == swappedAmount`, ensuring fees are only taken when there is an actual relay to receive them.

### Proof of Concept
Foundry fork test plan:
1. Deploy `HinkalHelper`, `Hinkal`, `Wrapper`, mock/real LI.FI router, and `LifiExternalAction`; register it via `registerExternalAction`.
2. As an unprivileged EOA, deposit shielded input UTXO(s) for `inputToken`.
3. Generate a valid proof/`CircomData` for a swap transaction with: `relay = address(0)`, `originalSender = msg.sender`, `externalActionData.externalActionId` = LifiExternalAction id, `feeStructure.variableRate = 500` (5%) and `feeStructure.flatFee = 0`.
4. Call `Hinkal.transact(...)`.
5. Assert: `LifiExternalAction`/`ExternalActionSwap` contract's `outputToken` balance after the tx equals `totalFee` (nonzero) — i.e., fee tokens are stuck in the contract.
6. Assert: no relay address received any transfer (there is none — `relay == address(0)`).
7. Assert: the resulting shielded UTXO amount inserted equals `swappedAmount - totalFee`, confirming `totalFee` value was removed from the user's output but never delivered to any party, and cannot be swept out by any existing owner/admin function.

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

**File:** contracts/HinkalHelper.sol (L30-35)
```text
    function relayerIsValid(address relay) internal view {
        if (relay != address(0)) {
            require(tx.origin == relay, "Unauthorized relay");
            require(isRelayInList(relay), "Relay is not whitelisted");
        }
    }
```

**File:** contracts/HinkalHelper.sol (L166-171)
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

**File:** contracts/Hinkal.sol (L188-229)
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
            }
        }
        require(
            circomData.relay == address(0) || hasPaidToRelay,
            "relay not paid"
        );
```
