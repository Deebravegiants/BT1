### Title
Duplicate `address(0)` legs in `erc20TokenAddresses` cause `msg.value` and balance deltas to be double-counted, allowing unbacked shielded-ETH UTXOs to be minted - (File: contracts/Hinkal.sol / contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`Hinkal.transact` and `EmporiumUpgradeable.runAction` both compute `oldBalances`/`newBalances` (or `balancesBefore`/`balancesAfter`) once via `getBalancesForArray`, but then iterate `circomData.erc20TokenAddresses` per-index to verify the balance equation. Nothing in `dimensionsCheck`/`checkOnchainCreation` enforces uniqueness of token addresses in that array, so an attacker can list `address(0)` (native ETH) twice. Because the ETH balance snapshot is identical for both indices, and Hinkal.sol's address(0) branch unconditionally re-adds the *full* `msg.value` to `balanceDif` at every index that equals `address(0)`, the same real ETH deposit and the same real balance delta can independently satisfy two separate per-index balance equations, letting the attacker claim an extra, unbacked UTXO on the "second leg".

### Finding Description
The invariant that should hold is: **for the set of distinct tokens in a call, `Σ balanceDif(token) == Σ (amountChanges(token) + utxoAmount(token))`, with each unit of real ETH/token counted exactly once.**

In `Hinkal.transact`: [1](#0-0) 

`oldBalances`/`newBalances` are computed once via `getBalancesForArray(circomData.erc20TokenAddresses)` [2](#0-1) 
using per-entry lookups that, for `address(0)`, simply return `address(this).balance` regardless of index [3](#0-2) 

so if `erc20TokenAddresses` contains `address(0)` at two indices `i` and `k`, `oldBalances[i] == oldBalances[k]` and `newBalances[i] == newBalances[k]`. Since the address(0) branch computes `balanceDif = newBalances[idx] + msg.value - oldBalances[idx]` independently per index, both `balanceDif_i` and `balanceDif_k` evaluate to the *same full value* (correctly incorporating `msg.value` once each, but with no mechanism to prevent it being spent twice across the two indices). The subsequent per-index requirement
`balanceDif == (onChainCreation[idx] ? 0 : amountChanges[idx]) + utxoAmount` is checked **independently** for `i` and `k` — nothing subtracts what was already "used" at the other duplicate index.

The same aliasing exists inside `EmporiumUpgradeable.runAction`, which likewise snapshots `balancesBefore`/`balancesAfter` once and loops per index:
<cite repo="Alyssadaypin/Hinkal-Contracts-Circuits--

### Citations

**File:** contracts/Hinkal.sol (L78-90)
```text
            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }

            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );
```

**File:** contracts/Hinkal.sol (L97-146)
```text
            for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {
                int256 balanceDif;

                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
                } else {
                    balanceDif =
                        int256(newBalances[i]) -
                        int256(oldBalances[i]);
                }
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

**File:** contracts/Transferer.sol (L149-176)
```text
    function getERC20OrETHBalance(
        address _erc20TokenAddress
    ) internal view returns (uint256) {
        if (_erc20TokenAddress == address(0)) {
            return address(this).balance;
        } else {
            IERC20 outToken = IERC20(_erc20TokenAddress);
            return outToken.balanceOf(address(this));
        }
    }

    function getBalancesForArrayMemory(
        address[] memory erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
        }
    }

    function getBalancesForArray(
        address[] calldata erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
        }
    }
```
