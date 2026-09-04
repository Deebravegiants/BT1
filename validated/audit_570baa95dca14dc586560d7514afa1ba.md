### Title
Emporium's "Stateless Interaction" ops allow draining any ERC1155 (or other non-tracked) asset custodied by the contract - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes attacker-controlled `EmporiumOperation`s as arbitrary `op.endpoint.call{value: op.value}(op.callData)` where `msg.sender` inside that call is the Emporium contract itself. The only balance reconciliation (`balancesBefore`/`balancesAfter`) applies exclusively to `circomData.erc20TokenAddresses`, so any ERC1155 (or ERC721) asset that a victim's earlier stateless op left custodied in the Emporium contract is completely unprotected and can be pulled out by any later caller.

### Finding Description
The claimed equality — `balanceOf(Emporium, id) attributable to victim == balanceOf(attacker's own contribution)` — is broken because Emporium never establishes this equality in the first place for non-ERC20 assets.

`runAction` computes `balancesBefore`/`balancesAfter` only for `circomData.erc20TokenAddresses` via `getBalancesForArray` [1](#0-0) , and reconciles balance deltas per-index against `deltaAmountChanges` [2](#0-1) . `handleOut` only forwards these listed ERC20/ETH balance changes back to `msg.sender` (the caller of that transaction) [3](#0-2) . There is no equivalent accounting, allow-list, or sweep mechanism for ERC1155/ERC721 tokens — `Emporium` inherits `Transferer`'s generic, unrestricted `onERC1155Received`/`onERC1155BatchReceived` hooks that simply return the acceptance selector with no bookkeeping [4](#0-3) .

The op execution itself imposes almost no restriction on target/callData:
```
(success, err) = op.endpoint.call{value: op.value}(op.callData);
```
only `callHinkalWallet`/`doSendToRelay` selectors are blocked [5](#0-4) . Since this call is made *from* the Emporium contract, `msg.sender == address(emporium)` inside the target call. If a victim's earlier `EmporiumOperation` (e.g., wrapping a position/ticket/game asset) causes an ERC1155 token to be minted/transferred to `address(emporium)` and left there (there is no code path that automatically forwards ERC1155 balances out, unlike ERC20), any subsequent, unrelated attacker can submit their own valid Hinkal proof (for their own unrelated UTXOs/deposits, possibly with an empty `erc20TokenAddresses` array) whose `externalActionMetadata` decodes to an `EmporiumStack` containing an op:
```
op.endpoint = <ERC1155 token address>
op.invokeWallet = false
op.callData = abi.encodeWithSelector(IERC1155.safeTransferFrom.selector, address(emporium), attacker, id, amount, "")
```
Because `from == msg.sender == address(emporium)`, the ERC1155 standard's `isApprovedForAll`/`msg.sender == from` check passes trivially, and the token contract executes the transfer, moving the victim-linked asset to the attacker.

Existing guards do not catch this:
- `onlyAllowedRecipient` only checks that the caller of `runAction` is the registered Emporium/Hinkal external-action address, not what the internal ops touch [6](#0-5) .
- `verifyWallet`/EIP-712 signature checking only applies when `stack.signerAddress != address(0)` (stateful path); the stateless path used here requires no wallet signature at all [7](#0-6) .
- The circuit/`calldataHash` mechanism (`CircomDataBuilder.getHashedCalldata`, `performHinkalChecks`) only binds the proof to whatever `externalActionMetadata` the *prover* chooses — it never semantically constrains that metadata's contents, so an attacker generating their own proof for their own UTXOs is free to embed arbitrary `EmporiumOperation`s [8](#0-7) .
- `Hinkal.transact`'s balance-diff/slippage checks after `_externalTransact` only iterate over `circomData.erc20TokenAddresses` [9](#0-8) ; an ERC1155 token address is not (and cannot meaningfully be, since ERC1155 `balanceOf` has a different signature) included there, so the theft produces zero signal in Hinkal's/Emporium's accounting.

### Impact Explanation
Any ERC1155 (or other asset type not modeled by `erc20TokenAddresses`) balance sitting in the Emporium contract — deposited there as a side effect of a legitimate user's stateless op — is stealable in full by any unrelated, unprivileged attacker in a single transaction, with no counted loss anywhere in Hinkal's ledger. This is direct theft of a victim's asset held in custody by a Hinkal-registered external action, matching the Critical category ("direct theft of shielded or in-flight user funds" / assets moved by a call the wallet owner never authorised). It is fully repeatable for every ERC1155 id/amount left behind by any victim's op.

### Likelihood Explanation
Preconditions: (1) at least one prior transaction (by any user) must leave an ERC1155 balance custodied at `address(emporium)` — plausible given Emporium's design purpose of proxying arbitrary calls to arbitrary `endpoint` contracts on behalf of users' stealth identities; (2) the attacker only needs their own valid proof over their own UTXOs (or even zero UTXOs), full control over `externalActionMetadata`, and knowledge of the token/id sitting in Emporium (discoverable on-chain via `onERC1155Received` events / token balance). No privileged role, no victim key, no relay collusion required — well within the stated attacker capabilities. Attacker cost is a single transaction; the exploit is deterministic and repeatable per residual balance.

### Recommendation
- Do not allow `EmporiumOperation.endpoint.call` in the stateless path to target the ERC1155/ERC721 token contracts holding Emporium-custodied assets with `from == address(emporium)` unless explicitly authorized per-transaction and tied to the depositor's proof/UTXO.
- Either (a) forbid stateless ops from leaving any ERC721/ERC1155 balance in Emporium — force an atomic forward-out to the depositor's `msg.sender`/stealth address within the same `runAction` call (mirroring the ERC20 `handleOut` pattern), or (b) add an on-chain, per-asset ownership ledger (id → stealth address/committed owner) that must be checked and updated before any outgoing transfer of that asset is permitted.
- At minimum, add an allow-list of endpoints callable by stateless ops, and/or require that `op.callData`'s target/selector be constrained by the circuit's public inputs (e.g., part of `calldataHash` binding checked against a per-user commitment rather than freely chosen by the prover).

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (as registered external action), a `MockERC1155`.
2. "Victim" transaction: submit a valid Hinkal `transact` proof with `externalActionData.externalAddress = Emporium`, `externalActionMetadata` decoding to an `EmporiumStack` whose single stateless op calls `MockERC1155.mint(address(emporium), id, amount)` (simulating a wrapped position/ticket landing in Emporium). Assert `MockERC1155.balanceOf(emporium, id) == amount` after the tx, and that `Emporium.getBalancesForArray`-tracked ERC20 balances are unaffected (0 delta), i.e., the ERC1155 balance is invisible to Hinkal's balance-diff/slippage checks.
3. "Attacker" transaction: generate the attacker's own valid Hinkal proof over the attacker's own (possibly empty) `erc20TokenAddresses`/UTXOs, with `externalActionMetadata` decoding to an `EmporiumStack` whose op calls `MockERC1155.safeTransferFrom(address(emporium), attacker, id, amount, "")` with `endpoint = address(MockERC1155)`, `invokeWallet = false`.
4. Assert: `MockERC1155.balanceOf(emporium, id) == 0` and `MockERC1155.balanceOf(attacker, id) == amount` after the attacker's tx, while the attacker's `erc20TokenAddresses`/UTXO-based balance changes recorded by `Hinkal.transact` show zero corresponding registered outflow (no `amountChanges`/`utxoAmount` accounts for it) — demonstrating value left the protocol's custody with zero counted value conservation.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-88)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-151)
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

**File:** contracts/external-actions/ExternalActionBaseUpgradeable.sol (L39-46)
```text
    modifier onlyAllowedRecipient() {
        ExternalActionBaseStorage storage $ = _getExternalActionBaseStorage();
        require(
            $._isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
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

**File:** contracts/Hinkal.sol (L88-147)
```text
            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            OnChainCommitment[]
                memory onChainCommitments = new OnChainCommitment[](
                    utxoSet.length
                );
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
