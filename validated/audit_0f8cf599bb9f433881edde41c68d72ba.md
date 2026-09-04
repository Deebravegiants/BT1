### Title
Emporium `runAction` never tracks non-ERC20/ETH assets (e.g. NFTs) it holds, letting any unrelated `transact()` call drain them via CASE 2 (`invokeWallet:false`) — ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` only measures balance deltas over `circomData.erc20TokenAddresses` (ERC20/ETH) before and after executing arbitrary `EmporiumOperation`s, and CASE 2 stateless ops execute `op.endpoint.call(op.callData)` directly from the Emporium contract's own context with no restriction on target/selector other than blocking the two `HinkalWallet` selectors. If a victim's earlier Emporium action leaves an ERC721/ERC1155 asset owned by `address(Emporium)` itself, that asset is never accounted for or returned, and any later, completely unrelated attacker `transact()` can supply an `EmporiumStack` whose op calls `nftMarket.transferFrom(address(Emporium), attacker, tokenId)`. Since `msg.sender` seen by the NFT contract is `address(Emporium)` (the actual owner), the call succeeds and the balance/slippage checks — which only look at `circomData.erc20TokenAddresses` — see zero change and pass.

### Finding Description
The broken equality: **"NFT owner immediately after victim's Emporium purchase" should equal "victim's stealth-address-controlled position (i.e., value credited into Hinkal's off-chain accounting)"**. In fact, after a CASE 2 op that buys an NFT and leaves it on `address(Emporium)`, ownership is `address(Emporium)`, and Hinkal has no representation of it at all — the NFT is simply unaccounted collateral sitting in a shared contract.

Code path:
- `EmporiumUpgradeable.runAction` (contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:76-160) snapshots `balancesBefore`/`balancesAfter` only for `circomData.erc20TokenAddresses` via `getBalancesForArray` (contracts/Transferer.sol:169-176), and `handleOut` only ever moves out `circomData.erc20TokenAddresses[i]` (lines 162-184). Nothing in this function inspects `IERC721(nftMarket).ownerOf(tokenId)` or any NFT/1155 balance.
- CASE 2 (lines 102-113): `(success, err) = op.endpoint.call{value: op.value}(op.callData);` is fully attacker-controlled arbitrary call from `address(this)` (the Emporium), gated only against the `callHinkalWallet`/`doSendToRelay` selectors.
- `verifyWallet` (lines 302-349) only enforces a signature when `stack.signerAddress != address(0)`; if `signerAddress == address(0)` (an unauthenticated/"anyone" stack), it just marks the nonce used and returns — no owner/whitelist restriction on which endpoint/callData combination may run.
- `Hinkal.sol` `transact()` → `_externalTransact` (contracts/Hinkal.sol:234-261) lets **any** caller with a valid proof for their **own** UTXOs invoke `IExternalActionV2(externalAddress).runAction(circomData, deltaAmountChanges)` as long as `externalActionMap[externalActionId] == externalAddress`. `HinkalHelper.performHinkalChecks` (contracts/HinkalHelper.sol:208-236) only checks `getHashedCalldata(circomData) == circomData.calldataHash` — an internal consistency check the attacker computes themselves — never any semantic restriction on `externalActionMetadata` content.
- `Hinkal.sol` outer balance/slippage/utxo checks (lines 88-146) iterate only `circomData.erc20TokenAddresses`, so an attacker's `circomData` (their own, small/dummy token entry) shows `balanceDif == 0` on both sides and the checks pass trivially.

Exploit flow:
1. Victim calls `transact()` with `externalActionId` = Emporium, `EmporiumStack` op = `{endpoint: nftMarket, invokeWallet: false, callData: buyNFT(...)}` (CASE 2). NFT is purchased and, per the marketplace's transfer, ends up owned by `address(Emporium)` (accepted through `Transferer.onERC721Received`, contracts/Transferer.sol:19-26).
2. Attacker crafts their own valid proof/`CircomData` for their own funds (any `erc20TokenAddresses` unrelated to the NFT, e.g. a zero-delta dummy entry), sets `externalActionId` = Emporium, `EmporiumStack.signerAddress = address(0)`, op = `{endpoint: nftMarket, invokeWallet: false, callData: transferFrom(address(Emporium), attacker, tokenId)}`.
3. `runAction` executes the op via `op.endpoint.call(...)`; `nftMarket.transferFrom` sees `msg.sender == address(Emporium)` which is the actual owner, so the transfer succeeds.
4. All ERC20/ETH balance snapshots for the attacker's declared tokens are unchanged (`balanceChange == 0`), so `BalanceChangeShouldBePositive` and Hinkal's slippage/balance-diff checks pass trivially. No nullifier, root, or circuit constraint references the NFT at all.

### Impact Explanation
Critical — direct theft of a user-created position. The victim's shielded/quasi-shielded value (the NFT purchased through Hinkal's Emporium) is stolen outright by an unrelated attacker who never interacted with the victim's UTXOs, nullifiers, or proof. This is repeatable for every NFT/1155 asset that ever ends up custodied by the shared `EmporiumUpgradeable` contract via a CASE 2 op, and costs the attacker only their own dummy proof/transaction.

### Likelihood Explanation
Preconditions: some victim (or even a benign or accidental interaction) must leave an NFT/1155 asset owned by `address(Emporium)` via a CASE 2 op — plausible any time a marketplace `buy` call is issued without `invokeWallet` routing it through a personal `HinkalWallet`. Once that state exists, exploitation requires only a normal, low-cost `transact()` call by any unprivileged attacker with their own funds/proof; no special role or timing is needed, and it is fully repeatable for every stranded NFT.

### Recommendation
Either (a) forbid CASE 2 stateless ops from targeting/holding non-declared assets by tracking/whitelisting endpoints and requiring any NFT/1155 received by the Emporium during an action to be immediately forwarded to the acting user's stealth address / wallet in the same transaction, or (b) require all `EmporiumOperation`s that can result in Emporium custody of NFTs/1155s to go through CASE 1 (`invokeWallet:true`) with a per-user `HinkalWallet` as the actual holder (never `address(Emporium)`), and add an explicit check in `runAction` that `address(this)` never ends up owning any asset the action created (e.g., verify `ownerOf` for any minted/received NFT is not `address(Emporium)` after the ops loop, or disallow CASE 2 entirely for known NFT-transferring selectors).

### Proof of Concept
Foundry test plan:
1. Deploy a mock ERC721 `NftMarket` with `buyNFT(tokenId)` that mints/transfers `tokenId` to `msg.sender`, and standard `transferFrom`.
2. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, register Emporium as `externalActionId`.
3. Victim: build `CircomData`/proof for a `transact()` with `externalActionId = emporium`, `EmporiumStack.signerAddress = address(0)`, op `{endpoint: nftMarket, invokeWallet:false, value: price, callData: buyNFT(tokenId)}`. Assert `nftMarket.ownerOf(tokenId) == address(emporium)` after the call, and assert `balanceChange` for every entry in `circomData.erc20TokenAddresses` reconciles per Hinkal's checks (proving no revert on the intended path).
4. Attacker: build a second, unrelated `CircomData`/proof for their own dummy UTXO with `externalActionId = emporium`, `EmporiumStack.signerAddress = address(0)`, op `{endpoint: nftMarket, invokeWallet:false, value:0, callData: transferFrom(address(emporium), attacker, tokenId)}`.
5. Call `transact()` as attacker. Assert it does not revert, and assert `nftMarket.ownerOf(tokenId) == attacker` afterward, while every `balanceChange` for the attacker's declared `circomData.erc20TokenAddresses` entries is `0`, proving the NFT theft was invisible to all balance/slippage guards. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-160)
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

**File:** contracts/Transferer.sol (L19-26)
```text
    function onERC721Received(
        address,
        address,
        uint256,
        bytes calldata
    ) public pure returns (bytes4) {
        return IERC721Receiver.onERC721Received.selector;
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

**File:** contracts/Hinkal.sol (L96-147)
```text
            uint256 onChainCommitmentCounter = 0;
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
            }
```

**File:** contracts/Hinkal.sol (L234-261)
```text
    function _externalTransact(
        CircomData calldata circomData
    ) internal returns (UTXO[] memory) {
        require(
            externalActionMap[circomData.externalActionData.externalActionId] ==
                circomData.externalActionData.externalAddress &&
                circomData.externalActionData.externalAddress != address(0),
            "Unknown externalAddress"
        );

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

**File:** contracts/HinkalHelper.sol (L204-236)
```text
    ///@notice make performance checks for transactions
    ///@dev Check if transacaction is valid before making it
    ///@param circomData circom data
    ///@return inputForCircom
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
