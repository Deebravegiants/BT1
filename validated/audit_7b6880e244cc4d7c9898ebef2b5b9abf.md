### Title
Untracked ERC1155 transfers into Emporium are permanently stealable via unrestricted CASE 2 `op.endpoint.call` - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` only reconciles balances for `circomData.erc20TokenAddresses` (ERC20/ETH) via `getBalancesForArray`/`handleOut`, while `Transferer.onERC1155Received`/`onERC1155BatchReceived` unconditionally accept any ERC1155 transfer with no provenance bookkeeping. Any value a victim's CASE 2 op causes to land on Emporium as ERC1155 is never swept into a UTXO owned by `circomData.stealthAddressStructure`, and any later unprivileged caller can craft their own CASE 2 op invoking the same token's `safeTransferFrom(emporium, attacker, id, amount, "")`, which succeeds trivially because Emporium itself is `msg.sender` and `from`.

### Finding Description
Equality that must hold: after the victim's `transact()` completes, `IERC1155(token).balanceOf(emporium, id)` must equal `0`, with the value having been converted into a UTXO under `circomData.stealthAddressStructure`. Instead, because ERC1155 is outside the accounting model, `balanceOf(emporium, id) == victim's amount` and stays there indefinitely.

Path: `Hinkal.transact` → `_externalTransact` → `IExternalActionV2(EmporiumUpgradeable).runAction` [1](#0-0) . Inside `runAction`, the op stack is fully attacker-controlled data decoded from `circomData.externalActionData.externalActionMetadata` [2](#0-1) . `performHinkalChecks`/`getHashedCalldata` only checks internal hash consistency of the metadata bytes, never validates the *semantics* of `EmporiumStack.ops` (endpoint/callData) [3](#0-2) , so any caller with a valid proof over their *own* UTXOs can populate an arbitrary `EmporiumOperation[]`.

For CASE 2 (`op.invokeWallet == false` or `signerAddress == address(0)`), the only guard is a selector blacklist against re-entering `IHinkalWallet` methods; otherwise it performs a raw `op.endpoint.call{value: op.value}(op.callData)` as Emporium itself [4](#0-3) . Because Emporium is `msg.sender` for this call, any ERC1155 `safeTransferFrom(emporium, X, id, amount, data)` call passes the standard `_msgSender() == from` operator check trivially.

Post-loop accounting only iterates `circomData.erc20TokenAddresses` computing `balanceChange` and creating an output UTXO via `handleOut`/`transferERC20TokenOrETH` [5](#0-4) . `Transferer` (inherited by `EmporiumUpgradeable`) exposes `onERC1155Received`/`onERC1155BatchReceived` that unconditionally return the selector with no recorded owner/UTXO linkage [6](#0-5) . There is no ERC1155 entry in `getBalancesForArray`/`getERC20OrETHBalance`, which only branch on ETH-vs-ERC20 [7](#0-6) .

Consequently: (1) victim's transaction executes a CASE 2 op that results in an ERC1155 vault-share balance sitting on `Emporium`, with the victim's `circomData.erc20TokenAddresses` (per the stated precondition) not including that ERC1155 asset — no UTXO is minted for it, so it is neither returned to the victim nor represented as shielded value; (2) any subsequent unprivileged attacker submits their own `transact()` with a trivial/self-owned UTXO, targeting Emporium's registered `externalActionId`, with a CASE 2 `EmporiumOperation` whose `endpoint` is the ERC1155 contract and `callData` is `safeTransferFrom(emporium, attacker, id, amount, "")`. This call succeeds because `msg.sender == from == emporium`, and the attacker's own `circomData.erc20TokenAddresses`/`deltaAmountChanges` need not reference this token at all, so the `BalanceChangeShouldBePositive` guard (which only covers declared ERC20/ETH tokens) never triggers for it. The stranded ERC1155 balance is drained to the attacker.

None of the existing guards prevent this: `onlyAllowedRecipient` only restricts the caller of `runAction` to `Hinkal` itself, not what `Hinkal` is asked to relay on a user's behalf; `verifyWallet`/`usedMessages` only dedupe `emporiumMessage` values, not op contents; `performHinkalChecks`/`dimensionsCheck`/`checkOnchainCreation` validate nullifier/output-count/on-chain-creation invariants for the *declared* ERC20 token set, never ERC1155 assets; the circuit constraints (`inTotal + amountChanges === outTotal`, overflow checks) bind only the shielded-balance ledger for declared tokens, not arbitrary external call side effects.

### Impact Explanation
Direct theft of a victim's shielded value (ERC1155 vault shares) that was intended to become a Hinkal UTXO. Any unprivileged attacker who observes Emporium's ERC1155 balance can drain it with a single low-cost self-authored transaction, repeatable for every ERC1155 asset/id combination that ever gets stranded on Emporium by any user's CASE 2 op. This is Critical: direct theft of shielded user funds.

### Likelihood Explanation
Preconditions: a victim (or any dApp integration built on Emporium's generic CASE 2 call mechanism) performs an action whose resulting value is an ERC1155 token that is not included in the same transaction's `circomData.erc20TokenAddresses` — plausible for vault/lending protocols that mint positions as ERC1155 rather than ERC20. No privileged role, special timing, or race condition is required by the attacker: the stranded balance persists on-chain indefinitely until swept, and the attacker's own `transact()` requires only a proof over their own (even dust) UTXO. Cost is a single gas-only transaction; the exploit is fully repeatable across victims and token ids.

### Recommendation
Either (a) disallow CASE 2 `op.endpoint.call` targets/selectors that are ERC721/ERC1155 transfer-family functions unless `circomData` explicitly declares and reconciles the resulting non-fungible/semi-fungible balance (extend the balance-diffing model beyond ERC20/ETH to cover declared ERC1155 `(token, id)` pairs and mint a corresponding UTXO/commitment for any balance increase), or (b) remove Emporium's blanket ERC1155/ERC721 receiver-hook acceptance and instead require an explicit, provenance-recording deposit path (mirroring the ERC20 `deltaAmountChanges`/`handleOut` flow) before any such asset can be held by Emporium, rejecting unsolicited transfers by default.

### Proof of Concept
Foundry test outline:
1. Deploy a mock ERC1155 vault, `Hinkal`, `HinkalHelper`, and `EmporiumUpgradeable` (registered as an external action on `Hinkal`), with `EmporiumUpgradeable` added to `Hinkal`'s `_isAllowedRecipient`.
2. Victim step: generate a valid proof/`CircomData` for the victim's own UTXO where `externalActionData.externalActionId` = Emporium's id, `externalActionMetadata` decodes to an `EmporiumStack` with `signerAddress = address(0)` and one CASE 2 `EmporiumOperation` calling the mock ERC1155's `mint(emporium, id, amount)` (or `safeTransferFrom` from victim to emporium), and `circomData.erc20TokenAddresses` excludes the ERC1155 token. Call `hinkal.transact(...)`. Assert `mockERC1155.balanceOf(emporium, id) == amount` and no corresponding UTXO/commitment event was emitted for it.
3. Attacker step: with a separate, unrelated dust UTXO owned by the attacker, generate a second proof/`CircomData` whose Emporium `EmporiumStack` CASE 2 op calls `mockERC1155.safeTransferFrom(emporium, attacker, id, amount, "")`. Call `hinkal.transact(...)` as the attacker.
4. Assert `mockERC1155.balanceOf(attacker, id) == amount` (the victim's original amount) and `mockERC1155.balanceOf(emporium, id) == 0`, demonstrating full drain by an unrelated, unprivileged party.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-118)
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

            if (!success) {
                revert CallFailed(err);
            }
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-184)
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

**File:** contracts/HinkalHelper.sol (L208-236)
```text
    function performHinkalChecks(
        CircomData calldata circomData,
        Dimensions calldata dimensions,
        address sender
    ) external view returns (uint256[] memory) {
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
        relayerIsValid(circomData.relay);
        dimensionsCheck(circomData, dimensions);
        checkOnchainCreation(circomData);

        return
            CircomDataBuilder.formInputForCircom(
                block.chainid,
                hinkalAddress,
                circomData
            );
    }
```

**File:** contracts/Transferer.sol (L28-46)
```text
    function onERC1155Received(
        address,
        address,
        uint256,
        uint256,
        bytes calldata
    ) public pure returns (bytes4) {
        return IERC1155Receiver.onERC1155Received.selector;
    }

    function onERC1155BatchReceived(
        address,
        address,
        uint256[] calldata,
        uint256[] calldata,
        bytes calldata
    ) public pure returns (bytes4) {
        return IERC1155Receiver.onERC1155BatchReceived.selector;
    }
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
