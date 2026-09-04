## Analysis

**The claimed equality break:** The question posits that a negative `slippageValues[i]` could let `Hinkal.transact` accept `balanceDif < utxoAmount + amountChanges[i]` (i.e., mint shielded value without full backing) when a "zero-amount leg" in a LiFi batch strands the transaction due to a revert-on-zero-transfer token.

**Tracing the actual guard:** In `Hinkal.transact`, there are **two separate requires**, not one:

```
require(balanceDif >= circomData.slippageValues[i], "slippage param is violated");
...
require(
    balanceDif == (circomData.onChainCreation[i] ? int256(0) : circomData.amountChanges[i]) + int256(utxoAmount),
    "Balance Diff Should be equal to sum of onchain and offchain created commitments"
);
``` [1](#0-0) 

The slippage check is only a lower-bound sanity check — a **negative `slippageValues[i]`** merely loosens *that* check. It does **not** replace the second, hard **equality** check, which is computed from `newBalances`/`oldBalances` (real `balanceOf` snapshots taken via `getBalancesForArray`) versus `amountChanges[i] + utxoAmount` (the actual value backing minted UTXOs). This equality must hold *exactly* regardless of the slippage floor's value. So even if the floor "accepts a loss," the equality check still forces `balanceDif` to match the minted UTXO value precisely — there is no path where minted shielded value can exceed what was actually received. [2](#0-1) 

**On the "zero-amount leg strands the batch" premise:** Solidity's call semantics mean a revert anywhere in `_externalTransact` → `IExternalActionV2.runAction` → `ExternalActionSwap.swap` → `LifiExternalAction.callRouter` propagates and reverts the *entire* `transact` call atomically — there is no partial commit of state that could leave the vault under-collateralized while UTXOs are still minted. Additionally, the codebase already guards zero-value transfers with explicit `> 0` checks in the paths that matter: `sendToRelay` only transfers `if (relay != address(0) && actualAmount > 0)`, and `multiTransferFrom`/`_internalTransact` only call transfer when the delta amount is nonzero. [3](#0-2) [4](#0-3) [5](#0-4) 

In `LifiExternalAction.callRouter`, the swapped amount is derived from a direct before/after `balanceOf` diff around the router call, and this genuine amount is what gets transferred out and what backs the minted `UTXO` — so the value entering `utxoSet` is tied to the token's real balance delta, not an attacker-controlled claim. [6](#0-5) [7](#0-6) 

Since the equality `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` is checked against real on-chain balances every time — independent of the slippage floor's sign — there is no way for the described attack to make the vault mint shielded value that exceeds what it actually received; any divergence simply reverts the whole transaction.

### No vulnerability found for this question.

### Citations

**File:** contracts/Hinkal.sol (L110-146)
```text
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

**File:** contracts/Hinkal.sol (L172-225)
```text
    function _internalTransact(CircomData calldata circomData) private {
        bool hasPaidToRelay = false;
        for (uint64 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 deltaAmountChange = _calculateDeltaAmount(circomData, i);

            if (deltaAmountChange > 0) {
                require(
                    circomData.externalActionData.externalAddress == msg.sender,
                    "Deposit should come from the sender"
                );
                transferERC20TokenFromOrCheckETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    address(this),
                    uint256(circomData.amountChanges[i])
                );
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
```

**File:** contracts/Transferer.sol (L130-147)
```text
    function multiTransferFrom(
        address[] memory erc20TokenAddresses,
        address _from,
        address _to,
        uint256[] memory amounts
    ) internal returns (bool) {
        for (uint64 i = 0; i < erc20TokenAddresses.length; i++) {
            if (amounts[i] > 0) {
                transferERC20TokenFromOrCheckETH(
                    erc20TokenAddresses[i],
                    _from,
                    _to,
                    amounts[i]
                );
            }
        }
        return true;
    }
```

**File:** contracts/Transferer.sol (L169-176)
```text
    function getBalancesForArray(
        address[] calldata erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
        }
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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L88-101)
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
```
