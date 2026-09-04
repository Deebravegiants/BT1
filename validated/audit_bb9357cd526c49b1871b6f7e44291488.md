### Title
Emporium withdrawals through the `signerAddress` code path skip the protocol's percentage-based relay fee - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.payRelayFees()` applies two different fee schedules to the exact same economic event — funds leaving the shielded pool through Emporium. When `stack.signerAddress == address(0)`, the full fee (flat fee **plus** `variableRate` percentage of the withdrawn amount) is charged via `IHinkalHelper.calculateRelayFee`. When `stack.signerAddress != address(0)`, only the flat fee is charged; the percentage component is silently dropped. Because `signerAddress` is a value the transaction's own author freely chooses (and signs) for their own withdrawal, any unprivileged user can select the `signerAddress != address(0)` branch purely to avoid the percentage-based protocol/relay fee — the same "split-the-operation-to-skip-part-of-the-fee" pattern described in the report, but here achieved by choosing a code branch instead of splitting calls.

### Finding Description
`runAction` decodes an `EmporiumStack` (`v, r, s, signerAddress, ops, maxFee, deadline`) from `circomData.externalActionData.externalActionMetadata` and passes `stack.signerAddress` into `payRelayFees`: [1](#0-0) 

`payRelayFees` computes the fee for each withdrawn (negative-delta) token differently depending on whether `signerAddress` is zero: [2](#0-1) 

- `signerAddress == address(0)`: `relayFee = calculateRelayFee(sumAbs, flatFee, variableRate)` → charges flat fee **and** the `variableRate` cut of the entire withdrawn amount, matching `RelayStore.calculateRelayFee`: [3](#0-2) 
- `signerAddress != address(0)`: `relayFee = flatFee` only — the percentage component is never applied to `sumAbs`.

`verifyWallet` only checks that the caller can produce a valid ECDSA signature recovering to `signerAddress`, and that `flatFee <= maxFee`; it never checks/limits the *percentage* fee nor requires `signerAddress` to correspond to a real, funded `HinkalWallet`: [4](#0-3) 

Whether the wallet path is actually used for any given operation is independent of `stack.signerAddress`: individual ops choose `invokeWallet` per-operation, and CASE 2 (stateless, direct `op.endpoint.call`) is used whenever `invokeWallet` is false, regardless of `signerAddress`: [5](#0-4) 

So a user can supply an `EmporiumStack` with `signerAddress` set to any address they can sign for (even a plain EOA with no wallet contract deployed), have all `ops` be stateless calls (`invokeWallet = false`), and still hit the `signerAddress != address(0)` branch in `payRelayFees`, which charges only `flatFee` on the withdrawal instead of `flatFee + variableRate·amount`. If `feeStructure.flatFee` is 0 for the withdrawn/non-fee token (`flatFee = isFeeToken ? feeStructure.flatFee : 0`), the relay fee for that token is entirely zero — `payRelay` also short-circuits when `relayFee == 0`, so no `doSendToRelay`/wallet interaction is even attempted: [6](#0-5) 

This breaks the intended equality that the fee charged should equal `flatFee + variableRate * withdrawnAmount` for every unit of value that leaves the shielded pool via Emporium; instead the amount actually collected depends only on which optional field (`signerAddress`) the withdrawer chose to populate for their own transaction — directly analogous to the reported "add premium doesn't collect fees" pattern where fee coverage depends on which entry point is used rather than on the economic size of the operation.

### Impact Explanation
This results in permanent, systemic underpayment (or complete avoidance, when `flatFee == 0` for the relevant token) of the protocol/relayer's percentage-based fee on Emporium withdrawals. Per the stated impact rubric this is theft/permanent loss of protocol/relay fees (High) — every user withdrawing through Emporium can route around the variable-rate fee simply by populating `signerAddress` with their own address and using stateless ops, at the cost of nothing beyond the (possibly zero) flat fee.

### Likelihood Explanation
High likelihood: exploiting this requires no privileged role, no external contract deployment, and no interaction with `HinkalWallet` at all — only choosing a non-zero `signerAddress` the caller can sign for when building their own Emporium transaction (the same way a normal user already builds `EmporiumStack`). It is a pure choice of an optional, self-controlled parameter, not a race condition or edge case.

### Recommendation
Apply the same `flatFee + variableRate` fee formula (`calculateRelayFee`) regardless of `signerAddress`. If the wallet-signed path is intentionally meant to only bear a flat fee because a distinct fee-collection mechanism is expected elsewhere, that mechanism should be enforced on-chain (e.g., requiring `signerAddress` to be a verified `HinkalWallet` contract that also settles the variable-rate portion), rather than silently dropping the percentage fee whenever a non-zero `signerAddress` is supplied.

### Proof of Concept
1. User builds a normal Hinkal shielded withdrawal via Emporium for a large token amount (`deltaAmountChanges[i] < 0` for the withdrawn token).
2. In the `externalActionMetadata`, the user encodes an `EmporiumStack` where:
   - `signerAddress` = an address they hold the private key for (no need to deploy an actual `IHinkalWallet` contract).
   - all `ops[].invokeWallet = false` (purely stateless calls, e.g. simple no-op/self-transfer endpoint calls or the actual desired external calls).
   - `v, r, s` = a valid EIP-712 signature over `EMPORIUM_SIGNATURE_TYPEHASH` recovering to `signerAddress`.
   - `maxFee` ≥ `feeStructure.flatFee`.
3. Submit the transaction/proof as usual.
4. In `payRelayFees`, since `signerAddress != address(0)`, `relayFee = flatFee` only is charged on the withdrawn amount — the `variableRate` percentage that would otherwise apply (per `RelayStore.calculateRelayFee`) is never collected, and if `flatFee` for that token is 0, no fee is paid at all.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-90)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );

        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);

```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-118)
```text
        for (uint256 i = 0; i < stack.ops.length; i++) {
            EmporiumOperation memory op = stack.ops[i];

            bool success;
            bytes memory err;

            // CASE 1: Stateful Interaction
            if (op.invokeWallet && stack.signerAddress != address(0)) {
                (success, err) = IHinkalWallet(stack.signerAddress)
                    .callHinkalWallet(op.endpoint, op.callData, op.value);
            }
            // CASE 2: Stateless Interaction
            else {
                bytes4 selector = bytes4(op.callData);
                if (
                    selector == IHinkalWallet.callHinkalWallet.selector ||
                    selector == IHinkalWallet.doSendToRelay.selector
                ) {
                    revert UnauthorizedWalletCall();
                }

                (success, err) = op.endpoint.call{value: op.value}(op.callData);
            }

            if (!success) {
                revert CallFailed(err);
            }
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L201-238)
```text
    function payRelayFees(
        CircomData calldata circomData,
        address signerAddress,
        int256[] calldata deltaAmountChanges
    ) internal {
        FeeStructure calldata feeStructure = circomData.feeStructure;

        bool foundToken = false;

        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            // tokens deposited into Emporium are not charged
            if (deltaAmountChanges[i] >= 0) {
                continue;
            }

            address erc20TokenAddress = circomData.erc20TokenAddresses[i];
            bool isFeeToken = erc20TokenAddress == feeStructure.feeToken;

            if (isFeeToken) {
                foundToken = true;
            }

            uint256 relayFee = 0;
            uint256 flatFee = isFeeToken ? feeStructure.flatFee : 0;

            if (signerAddress == address(0)) {
                uint256 sumAbs = uint256(-deltaAmountChanges[i]);

                EmporiumStorageVars storage $ = _getEmporiumStorage();
                relayFee = $._hinkalHelper.calculateRelayFee(
                    sumAbs,
                    flatFee,
                    feeStructure.variableRate
                );
            } else {
                relayFee = flatFee;
            }

```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L262-282)
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

        if (signerAddress == address(0)) {
            sendToRelay(relay, relayFee, erc20TokenAddress);
        } else {
            sendToRelayFromWallet(
                relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-349)
```text
    function verifyWallet(
        EmporiumStack memory stack,
        CircomData calldata circomData
    ) internal {
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
        }

        bytes32 hashedMessage = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    EMPORIUM_SIGNATURE_TYPEHASH,
                    circomData.emporiumMessage,
                    _hashEmporiumOps(stack.ops),
                    stack.maxFee,
                    stack.deadline
                )
            )
        );

        (address recoveredAddress, ECDSA.RecoverError err) = ECDSA.tryRecover(
            hashedMessage,
            stack.v,
            stack.r,
            stack.s
        );
        bool verified = err == ECDSA.RecoverError.NoError &&
            recoveredAddress == stack.signerAddress;
        if (!verified) {
            revert InvalidSignature();
        }

        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
    }
```

**File:** contracts/RelayStore.sol (L59-68)
```text
    function calculateRelayFee(
        uint256 balance,
        uint256 flatFee,
        uint256 variableRate
    ) public pure returns (uint256 relayFee) {
        require(balance >= flatFee, "Relay Fee is over withdraw amount");
        uint256 recipientAmount = ((10000 - variableRate) *
            (balance - flatFee)) / 10000;
        relayFee = balance - recipientAmount;
    }
```
