### Title
Emporium's stateless external calls can attribute a user's collateral/position to the shared Emporium contract, allowing another user to later drain it — (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction()` lets a signed (or relayer-submitted) stack of `EmporiumOperation`s make arbitrary calls to any `op.endpoint` directly from the Emporium contract itself ("CASE 2: Stateless Interaction"), with no allow-list on `endpoint` beyond blocking two specific `IHinkalWallet` selectors. This mirrors the `SiloGateway.borrowAsset()` bug class: when the target protocol records collateral/debt/position ownership against `msg.sender` rather than against a per-user identity, that state becomes attributed to the single, shared Emporium contract address used by every Hinkal user, not to the depositing user's wallet.

### Finding Description
`_externalTransact()` in `Hinkal.sol` moves ERC20 tokens to `circomData.externalActionData.externalAddress` (the Emporium contract) before calling `runAction`: [1](#0-0) 

Inside `EmporiumUpgradeable.runAction()`, for `invokeWallet == false` (or `signerAddress == address(0)`), the operation is executed directly by the Emporium contract against an arbitrary `op.endpoint`: [2](#0-1) 

Post-call accounting is purely ERC20-balance-diff based, via `getBalancesForArray`/`handleOut`, comparing before/after balances of `circomData.erc20TokenAddresses`: [3](#0-2) [4](#0-3) 

If `op.endpoint` is a lending/collateral protocol that records the depositor/borrower as `msg.sender` (exactly the `FraxLendPair._addCollateral(msg.sender, amount, borrower)` pattern cited in the report), the resulting collateral or debt position is opened against the Emporium contract address — a single address shared by every user of the protocol, not the depositing user's HinkalWallet or EOA. There is no per-user isolation for CASE 2 calls (unlike CASE 1, `invokeWallet`, which routes through the user's own `HinkalWallet` instance via `callHinkalWallet`).

Because the balance-diff equation only reasons about ERC20 token deltas on `circomData.erc20TokenAddresses` for the *current* transaction, it cannot see or protect the durable state left behind at the external protocol (e.g., `userCollateralBalance[emporium] += amount`). Any other Hinkal user can subsequently submit their own `EmporiumStack` with an op targeting the same external protocol (e.g., a withdraw/redeem call) that pays out to `msg.sender == Emporium`; the resulting positive ERC20 balance delta will be attributed to *that* caller's transaction and minted as a new UTXO for them via `handleOut`, even though the underlying collateral was deposited by a different, earlier user.

This breaks the balance equality the finding rules describe: value is moved by an external action (into a shared external-protocol position keyed by the Emporium's own address) but is not counted/isolated per-user in Hinkal's balance equation, letting one user's shielded collateral be drained by another user's later transaction.

### Impact Explanation
This is Critical: it enables direct theft of another user's shielded funds (their deposited collateral ends up creditable to whichever user next interacts with the same external position through Emporium), matching the accepted impact category "direct theft of shielded or in-flight user funds."

### Likelihood Explanation
Likelihood depends entirely on which `endpoint` protocols get used with Emporium's stateless (non-wallet) op path. Since `runAction` places no restriction on `op.endpoint` beyond the two `IHinkalWallet` selector checks, any integration with a lending/collateral protocol that tracks positions by `msg.sender` (as `FraxLendPair` does, and as flagged as a real, encountered case in the original report) reproduces the issue as soon as it is wired into an `EmporiumOperation`.

### Recommendation
For any external protocol integrated via Emporium's stateless call path, verify that it supports specifying a distinct beneficiary/borrower/owner separate from `msg.sender`, or force such integrations through the per-user `invokeWallet`/`HinkalWallet` path so that any resulting position is opened against the user's own dedicated wallet contract rather than the shared Emporium contract address. Alternatively, maintain and check on-chain accounting of which user is entitled to any external position opened via `op.endpoint.call` from Emporium.

### Proof of Concept
1. User A submits an `EmporiumStack` with `invokeWallet = false`, whose `op.endpoint` is a lending protocol (e.g., FraxLend-like) `addCollateral`-style function; tokens are pulled from the Hinkal shielded pool into Emporium and then supplied as collateral, recorded internally as `userCollateralBalance[Emporium] += amount`.
2. Emporium's balance-diff step (`getBalancesForArray` before/after) sees the ERC20 balance leave Emporium into the lending protocol; no UTXO is minted back to User A for this leg (consistent with intended collateral deposit), but the position is now owned by the Emporium contract address, not User A.
3. User B (any other Hinkal user) later submits an `EmporiumStack` with `op.endpoint` calling the same lending protocol's withdraw/redeem function, which pays out to `msg.sender == Emporium`.
4. Emporium's post-call balance diff shows a positive ERC20 balance increase attributable to User B's transaction; `handleOut` mints a new UTXO to User B for that amount.
5. User B has now redeemed User A's collateral as their own shielded balance, while User A's original deposit is unrecoverable — direct theft of shielded funds via the shared, unauthenticated external-protocol identity used by Emporium's stateless call path.

### Citations

**File:** contracts/Hinkal.sol (L244-261)
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

        return
            IExternalActionV2(circomData.externalActionData.externalAddress)
                .runAction(circomData, deltaAmountChanges);
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-113)
```text
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-160)
```text
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

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
        }

        return utxoSet;
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L162-184)
```text
    function handleOut(
        int256 balanceChange,
        CircomData calldata circomData,
        uint256 i
    ) internal returns (UTXO memory outUtxo) {
        // total change can be less than zero if there was some balance before the call -> that's why we have <=
        if (balanceChange <= 0) {
            return outUtxo;
        }

        transferERC20TokenOrETH(
            circomData.erc20TokenAddresses[i],
            msg.sender,
            uint256(balanceChange)
        );

        outUtxo = UTXO(
            uint256(balanceChange),
            circomData.erc20TokenAddresses[i],
            circomData.stealthAddressStructure,
            circomData.timeStamp
        );
    }
```
