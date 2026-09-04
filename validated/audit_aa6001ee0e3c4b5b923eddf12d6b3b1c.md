[1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/external-actions/swaps/LifiExternalAction.sol (L29-33)
```text
        } else {
            approveUnlimited(inputToken, router);
            (bool success, ) = router.call(externalActionMetadata);
            require(success, "LI.FI swap failed: erc-20 token");
        }
```

**File:** contracts/HinkalWrapper.sol (L106-108)
```text
        for (uint256 k = 0; k < uniqueCount; k++) {
            approveERC20Token(uniqueTokens[k], hinkal, uniqueAmounts[k]);
        }
```

**File:** contracts/Hinkal.sol (L68-80)
```text
        {
            if (circomData.hookData.preHookContract != address(0)) {
                IPreTransactHook transactHook = IPreTransactHook(
                    circomData.hookData.preHookContract
                );
                transactHook.preTransact(circomData);
            }

            UTXO[] memory utxoSet;

            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );
```
