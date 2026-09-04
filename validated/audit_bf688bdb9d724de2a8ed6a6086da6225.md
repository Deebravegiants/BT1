## Title
Swap external action always deducts a Hinkal/relay fee from user output but drops it permanently when `circomData.relay == address(0)` — (File: `contracts/external-actions/swaps/ExternalActionSwap.sol`)

### Summary
`ExternalActionSwap.swap` unconditionally computes a variable-rate "hinkal fee" (and, when the fee token differs from the output token, a flat relay fee taken out of the input side) and subtracts both from the amount credited back to the user's shielded UTXO. The fee is only actually transferred if `sendToRelay` sees a non-zero `circomData.relay`. Elsewhere in the protocol (`Hinkal.sol._internalTransact`), `circomData.relay == address(0)` is an explicitly supported, valid mode meaning "no relay fee is charged." `ExternalActionSwap` does not honor that invariant: it still deducts the fee from the user's output, but because the destination (`relay`) is the zero address, the deducted tokens are simply never sent anywhere and are left stranded in the `ExternalActionSwap` contract's own balance forever.

### Finding Description
In `swap()`: [1](#0-0) 

- `hinkalFee` is computed via `hinkalHelper.calculateRelayFee(swappedAmount, 0, circomData.feeStructure.variableRate)` regardless of whether a relay is present.
- `sendToRelay` (in `Transferer.sol`) only performs a transfer when `relay != address(0)`: [2](#0-1) 

- If `circomData.relay == address(0)`, both `sendToRelay` calls become no-ops, but `totalFee` (`hinkalFee`, plus `relayFee` if `feeToken == outputToken`) is still subtracted when computing `amountToSendToHinkal = swappedAmount - totalFee`, and that `amountToSendToHinkal` (not the full `swappedAmount`) is what gets transferred back to `msg.sender` (Hinkal) and encoded into the new UTXO. The `totalFee` amount of tokens is left sitting in the `ExternalActionSwap` contract balance, uncounted by any UTXO and unclaimable by anyone.

This breaks the same equality class as the referenced report: a fee/portion is computed and deducted from the value the user is credited with, but the configured destination address is zero, so the deducted value is not delivered anywhere and is lost from the system's accounted balance.

By contrast, the core protocol path treats `relay == address(0)` as "no fee" rather than "fee computed but undeliverable": [3](#0-2) 

Here the fee block (and thus any relay fee) is skipped entirely when `circomData.relay == address(0)` — the full `sumAbs` goes to the recipient, and `hasPaidToRelay` is not required. `ExternalActionSwap` does not replicate this "skip fee when no relay" guard, causing a divergence that leads to fund loss in the swap path specifically.

### Impact Explanation
Every swap performed through `ExternalActionSwap` with `circomData.relay == address(0)` (a legitimate, protocol-supported configuration used when no relay fee is intended) permanently strands the computed `hinkalFee` (and, when applicable, `relayFee`) tokens inside the `ExternalActionSwap` contract. These tokens are never transferred to the user, the relay, or any treasury, and are not represented by any UTXO/commitment, so they become permanently frozen protocol/relay fee value — matching the High-severity impact category of permanent freezing of protocol/relay fees.

### Likelihood Explanation
This triggers on any normal, unprivileged use of the swap external action whenever the prover/relayer sets `circomData.relay = address(0)` — no special conditions, admin privileges, or malicious relayer collusion are required. Since `relay == address(0)` is explicitly a first-class, supported value elsewhere in the protocol (see `Hinkal.sol` above), it is reasonably likely to occur in normal operation (e.g., self-relayed/gasless-fee-free transactions).

### Recommendation
Guard the fee computation and deduction in `ExternalActionSwap.swap` the same way `Hinkal._internalTransact` does: skip computing/deducting `hinkalFee`/`relayFee` entirely when `circomData.relay == address(0)`, so `amountToSendToHinkal` equals the full `swappedAmount` and no value is silently dropped. Alternatively, if a "protocol fee" is intended to be collected even without a relay, route it to an explicit, always-valid treasury address instead of conditionally through `sendToRelay`.

### Proof of Concept
1. User builds a swap transaction through `Hinkal.transact` → `_externalTransact` → `ExternalActionSwap.runAction`/`swap`, setting `circomData.relay = address(0)` and `circomData.feeStructure.variableRate = X > 0` (a valid, circuit-accepted combination since `relay` and `feeStructure` are independent public inputs).
2. `swap()` executes the router call, computes `swappedAmount`, then `hinkalFee = calculateRelayFee(swappedAmount, 0, X) > 0`.
3. Both `sendToRelay(address(0), ..., outputToken)` calls no-op because `relay == address(0)`.
4. `amountToSendToHinkal = swappedAmount - hinkalFee` is transferred to `msg.sender` (Hinkal) and becomes the new UTXO amount; the `hinkalFee` worth of `outputToken` remains in `ExternalActionSwap`'s token balance, uncounted by any UTXO, nullifier, or transfer — permanently stuck.

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
