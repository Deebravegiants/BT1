## Analog Found: Fee Always Deducted in `ExternalActionSwap::swap` Regardless of Whether a Relay Exists [1](#0-0) 

### Title
`ExternalActionSwap::swap` always deducts `hinkalFee`/`relayFee` from swap output even when `circomData.relay == address(0)`, permanently freezing that value in the contract - (File: contracts/external-actions/swaps/ExternalActionSwap.sol)

### Summary
`ExternalActionSwap::swap` unconditionally computes `hinkalFee` from `circomData.feeStructure.variableRate` and subtracts `totalFee` (`hinkalFee` + conditionally `relayFee`) from `swappedAmount` before forwarding the remainder to the caller (Hinkal). This mirrors the reported `DepositManager::getRewards` bug class: a fee is subtracted from the distributable amount unconditionally, even in the case where the party the fee is meant for (the relay) doesn't exist, so the deducted value is never paid out to anyone and is permanently stuck.

### Finding Description
In `Hinkal::_internalTransact`, the relay fee is only computed and moved when `circomData.relay != address(0)`: [2](#0-1) 

Likewise `EmporiumUpgradeable::payRelay` guards the transfer with `if (relay == address(0) || relayFee == 0) return;`: [3](#0-2) 

`Transferer::sendToRelay` itself is a no-op when `relay == address(0)`: [4](#0-3) 

However, `ExternalActionSwap::swap` computes `hinkalFee` and builds `totalFee` unconditionally, with no check on `circomData.relay`:
```solidity
uint256 relayFee = circomData.feeStructure.flatFee;
uint256 hinkalFee = hinkalHelper.calculateRelayFee(
    swappedAmount,
    0,
    circomData.feeStructure.variableRate
);

if (circomData.feeStructure.feeToken == outputToken) {
    sendToRelay(circomData.relay, relayFee + hinkalFee, outputToken);
} else {
    sendToRelay(circomData.relay, relayFee, circomData.feeStructure.feeToken);
    sendToRelay(circomData.relay, hinkalFee, outputToken);
}

uint256 totalFee = hinkalFee +
    (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
uint256 amountToSendToHinkal = swappedAmount - totalFee;

transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);
``` [5](#0-4) 

When `circomData.relay == address(0)` (a legitimate case — `Hinkal::_externalTransact` never validates `circomData.relay`, unlike `_internalTransact`), `sendToRelay` silently does nothing because of its internal `relay != address(0)` guard, so `hinkalFee` (and `relayFee`, if `outputToken == feeToken`) is never transferred anywhere. Yet `amountToSendToHinkal` still has `totalFee` subtracted from `swappedAmount`, and only `amountToSendToHinkal` is forwarded back to Hinkal via `transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal)` and represented in the resulting `UTXO`: [6](#0-5) 

The `totalFee` portion of `swappedAmount` remains stranded in the `ExternalActionSwap` contract's ERC20/ETH balance — never credited to the user's shielded UTXO, never paid to any relay. This breaks the balance equality the whole shielded-pool design depends on: `sum(user shielded UTXOs) == pool's on-chain token balance`. Here, real swapped value leaves the "circuit-accounted" side (it's not represented in the outgoing UTXO nor returned to the user) while remaining physically in the contract, unbacked by any UTXO and unclaimable by anyone.

### Impact Explanation
This causes permanent freezing of a percentage (`variableRate`, in basis points) of every swap's output whenever a user submits the swap without a relay (`circomData.relay == address(0)`), which is an explicitly supported, unprivileged path since `_externalTransact` places no restriction on `circomData.relay`. The frozen value is not recoverable by the user, the "relay" (which doesn't exist), or the protocol, matching the High severity bucket ("permanent freezing of protocol/relay fees" / "temporary freezing of user funds" — here it is the user's own swap proceeds that get permanently stuck since they were never returned).

### Likelihood Explanation
High likelihood: it requires no special conditions or privilege — any unprivileged EOA constructing a valid proof/circuit input for a swap through `ExternalActionSwap` with `circomData.relay = address(0)` (self-relaying, i.e. not using a third-party relayer) and any non-zero `circomData.feeStructure.variableRate` will trigger this loss on every such transaction.

### Recommendation
Gate the `hinkalFee`/`relayFee` computation and the `totalFee` deduction on `circomData.relay != address(0)`, mirroring the pattern already used in `Hinkal::_internalTransact` and `EmporiumUpgradeable::payRelay`:
```solidity
uint256 relayFee = 0;
uint256 hinkalFee = 0;
if (circomData.relay != address(0)) {
    relayFee = circomData.feeStructure.flatFee;
    hinkalFee = hinkalHelper.calculateRelayFee(
        swappedAmount,
        0,
        circomData.feeStructure.variableRate
    );
    // ... send to relay as before
}
uint256 totalFee = hinkalFee + (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
uint256 amountToSendToHinkal = swappedAmount - totalFee;
```
This ensures the fee is only deducted from the amount returned to the user when there is actually a relay to receive it.

### Proof of Concept
1. User builds a valid shielded-swap proof/`CircomData` calling `ExternalActionSwap::runAction` → `swap`, with `circomData.relay = address(0)` (self-submitted transaction, no relayer involved) and `circomData.feeStructure.variableRate = 200` (2%, arbitrary nonzero value the user/prover is free to set since it's not enforced to be zero when `relay == 0`).
2. `swap()` executes the router call, computing `swappedAmount`.
3. `hinkalFee = calculateRelayFee(swappedAmount, 0, 200)` = 2% of `swappedAmount`.
4. Because `circomData.relay == address(0)`, both `sendToRelay` calls are no-ops per `Transferer::sendToRelay`'s guard.
5. `totalFee = hinkalFee` (nonzero) is still subtracted: `amountToSendToHinkal = swappedAmount - hinkalFee`.
6. Only `amountToSendToHinkal` is transferred back to Hinkal and represented in the outgoing `UTXO`; the `hinkalFee` portion of `swappedAmount` remains in the `ExternalActionSwap` contract's token balance, unbacked by any UTXO and unrecoverable by the user, relay, or protocol admin through any function in the contract.

### Citations

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L63-93)
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
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L95-101)
```text
        utxoSet = new UTXO[](1);
        utxoSet[0] = UTXO({
            amount: amountToSendToHinkal,
            erc20Address: outputToken,
            stealthAddressStructure: circomData.stealthAddressStructure,
            timeStamp: block.timestamp
        });
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L262-271)
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
