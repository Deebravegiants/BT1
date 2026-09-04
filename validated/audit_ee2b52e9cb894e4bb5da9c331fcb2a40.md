### No vulnerability found for this question.

**Reasoning basis:**

`DepositOnChainUtxosExternalAction.runAction` does not use any "residual/dust balance" accounting pattern. Unlike `EmporiumUpgradeable.runAction`/`handleOut` (which do `balancesBefore`/`balancesAfter` diffing and hand out whatever balance sits in the action contract, including pre-existing dust), this action:

1. Requires `deltaAmounts[i] == 0` for every token [1](#0-0) , so `Hinkal._externalTransact` never pushes funds into this action's address for it (a negative `deltaAmountChanges[i]` there would pre-transfer to `externalAddress` and then this `require` would revert the whole atomic tx) [2](#0-1) .
2. Pulls tokens directly from `userAddress` to `msg.sender` (i.e. the Hinkal contract itself, since Hinkal is the external caller), not to the action contract: `transferERC20TokenFrom(tokenAddress, userAddress, msg.sender, tokenTotal)` [3](#0-2) .
3. Never reads `getBalancesForArray`/`getERC20OrETHBalance` on itself, never calls `handleOut`, and the UTXO amounts minted are exactly the caller-supplied `utxoAmounts` from `externalActionMetadata` — completely independent of whatever token balance the action contract itself happens to hold [4](#0-3) .

Because the function neither reads nor moves the action contract's own balance, there is no code path by which a pre-existing dust balance in the action (from a prior fee-on-transfer shortfall or any other source) can be captured by an attacker through this function. The claimed invariant break ("tokens leaving an action == -deltaAmountChanges Hinkal sent it") is not violated because no tokens ever leave the action contract in this flow at all — funds move straight from the depositing user to the Hinkal contract, bypassing the action's balance entirely.

### Citations

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L49-53)
```text
        for (uint256 i = 0; i < tokenCount; i++) {
            require(
                deltaAmounts[i] == 0,
                "DepositOnChainUtxosExternalAction: Delta amount must be zero"
            );
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L56-73)
```text
            uint256 tokenTotal = 0;

            for (uint256 j = 0; j < utxoAmounts[i].length; j++) {
                uint256 amount = utxoAmounts[i][j];
                require(
                    amount > 0,
                    "DepositOnChainUtxosExternalAction: UTXO amount must be positive"
                );
                tokenTotal += amount;

                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
            }
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L75-82)
```text
            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
```

**File:** contracts/Hinkal.sol (L244-256)
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
```
