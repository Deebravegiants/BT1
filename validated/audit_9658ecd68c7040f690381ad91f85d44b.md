## Title
Emporium wallet-signed withdrawals bypass the variable-rate protocol/relay fee - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

## Summary
`EmporiumUpgradeable.payRelayFees` computes the relay/protocol fee differently depending on whether the Emporium operation is signed by a `HinkalWallet` (`signerAddress != address(0)`) or executed directly (`signerAddress == address(0)`). In the wallet-signed branch, the fee charged is hardcoded to `flatFee` only, completely dropping the `variableRate` component of `circomData.feeStructure` that is applied in the non-wallet branch.

## Finding Description
`payRelayFees` branches on `signerAddress`: [1](#0-0) 

When `signerAddress == address(0)`, the fee is correctly computed via `calculateRelayFee(sumAbs, flatFee, feeStructure.variableRate)`, which applies the percentage-based `variableRate` on top of the flat fee, mirroring the logic used elsewhere in the protocol (e.g. `Hinkal._internalTransact`) [2](#0-1)  and `ExternalActionSwap.swap` [3](#0-2) .

However, when `signerAddress != address(0)` (i.e. the withdrawal is executed through a user-controlled `HinkalWallet` via a signed `EmporiumOperation`), `relayFee` is simply set to `flatFee`, and `feeStructure.variableRate` is never referenced at all. The wallet's `doSendToRelay` then transfers exactly that flat amount to the relay from the wallet's own balance [4](#0-3) .

The `feeStructure` (including `variableRate`) is bound into `calldataHash`, which is itself part of the signed message hash checked by the circuit (`getHashedCalldata2` includes `circomData.feeStructure`, and `getSignedMessageHash` includes `circomData.calldataHash`) [5](#0-4) [6](#0-5) . So the relayer/protocol *believes* it is entitled to a `variableRate`-based fee on the withdrawal (the value is cryptographically committed to and cannot be tampered with by the user), yet the code path that actually moves funds for wallet-signed Emporium ops never collects that portion. The `Emporium`'s own balance-equality checks in `runAction` (`balanceChange` vs `deltaAmountChanges`) never account for the missing variable fee either, since they only track token balances of the Emporium contract itself, not the wallet's balance [7](#0-6) .

This is the same bug class as the referenced Gondi finding: a fee that the accounting/signature layer expects to be applied (analogous to `protocolFee`) is silently replaced with a lesser value (analogous to hardcoded `0`) in one specific call path, breaking the equality between "fee the system believes was charged" and "fee actually transferred to the relay/protocol."

## Impact Explanation
Any user can route a withdrawal through the Emporium using a `HinkalWallet`-signed operation (`stack.signerAddress != address(0)`, using a wallet they legitimately control and sign for) and pay only the `flatFee`, permanently avoiding the `variableRate` percentage fee that the relay/protocol is otherwise entitled to on every other withdrawal path (direct Emporium call, `Hinkal._internalTransact`, `ExternalActionSwap`). This results in a permanent loss/freezing of protocol/relay fee revenue for any withdrawal that goes through this code path — satisfying the High severity bar ("theft or permanent freezing of protocol/relay fees").

## Likelihood Explanation
High likelihood: this requires no special privilege — any user who owns/deploys a `HinkalWallet` and can obtain a valid Emporium proof can trivially choose to route withdrawals via the wallet-signed path instead of the direct path, systematically avoiding variable-rate fees on every withdrawal.

## Recommendation
In `payRelayFees`, apply `calculateRelayFee(sumAbs, flatFee, feeStructure.variableRate)` (or the wallet-appropriate equivalent) in the `signerAddress != address(0)` branch as well, instead of only charging `flatFee`. If a different fee model is intentionally chosen for wallet-signed ops, this must be documented and safely accounted for elsewhere (e.g. via a distinct signed fee agreement), otherwise unify the fee computation across both branches so variable-rate is never skipped.

## Proof of Concept
1. User deploys/owns a `HinkalWallet` (`emporium` set to the deployed `EmporiumUpgradeable`).
2. User constructs a valid ZK proof + `CircomData` for a withdrawal with `circomData.relay != address(0)` and `circomData.feeStructure.variableRate > 0`, `feeStructure.flatFee` set to some value, targeting the Emporium external action with `stack.signerAddress = <their HinkalWallet>` and `invokeWallet = true` for the relevant op(s).
3. User signs the `EmporiumStack` EIP-712 message themselves (they are the wallet's authorized signer) — `verifyWallet` passes.
4. `runAction` executes `payRelayFees`, which since `signerAddress != address(0)`, computes `relayFee = flatFee` for the fee-token entry, skipping `calculateRelayFee` entirely — no variable-rate is deducted, contrary to `feeStructure.variableRate` bound in `calldataHash`/signed message.
5. Relay receives only the flat fee; the variable-rate fee that would otherwise be paid (compare with the `signerAddress == address(0)` path or `Hinkal._internalTransact`) is never collected, for any amount of tokens withdrawn.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-151)
```text
        payRelayFees(circomData, stack.signerAddress, deltaAmountChanges);

        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        UTXO[] memory utxoSet = new UTXO[](
            circomData.erc20TokenAddresses.length
        );

        uint256 utxoSetLength;

        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 balanceChange = int256(balancesAfter[i]) -
                int256(balancesBefore[i]);

            if (deltaAmountChanges[i] < 0) {
                balanceChange -= deltaAmountChanges[i];
                // this equation reads: total change of emporium balance = what was moved to emporium (-deltaAmountChange) + how emporium balance changed through tx (balanceChange)
            }

            // the only case when balanceChange can be < 0, when there were some funds on emporium before the call
            if (balanceChange < 0) {
                revert BalanceChangeShouldBePositive();
            }

            UTXO memory utxoOut = handleOut(balanceChange, circomData, i);

            if (utxoOut.amount > 0) {
                utxoSet[utxoSetLength++] = utxoOut;
            }
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L223-237)
```text
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

**File:** contracts/Hinkal.sol (L188-216)
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

**File:** contracts/external-actions/emporium/HinkalWallet.sol (L36-42)
```text
    function doSendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) external onlyEmporium {
        sendToRelay(relay, actualAmount, erc20TokenAddress);
    }
```

**File:** contracts/CircomDataBuilder.sol (L37-54)
```text
    function getHashedCalldata2(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.hookData,
                        circomData.encryptedOutputs,
                        circomData.onChainEncryptedOutput,
                        circomData.feeStructure,
                        circomData.onChainCreation,
                        circomData.originalSender,
                        circomData.extraData
                    )
                )
            );
    }
```

**File:** contracts/CircomDataBuilder.sol (L104-119)
```text
        uint256 hash1 = uint256(
            keccak256(
                abi.encode(
                    chainId,
                    verifyingContract,
                    circomData.rootHashHinkal,
                    _encodeTokenAddresses(circomData.erc20TokenAddresses),
                    _encodeAmountChanges(circomData.amountChanges),
                    circomData.timeStamp,
                    _flatUint256Matrix(circomData.inputNullifiers),
                    _flatUint256Matrix(circomData.outCommitments),
                    circomData.calldataHash,
                    emporiumMessage
                )
            )
        );
```
