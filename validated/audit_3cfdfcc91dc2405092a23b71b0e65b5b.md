### Title
Unrestricted CASE 2 `op.endpoint.call(op.callData)` in `EmporiumUpgradeable.runAction` allows theft of any asset (e.g. an LP NFT) left custodied at the Emporium contract - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction`'s "CASE 2: Stateless Interaction" branch performs `op.endpoint.call{value: op.value}(op.callData)` with only a selector blacklist (`callHinkalWallet`/`doSendToRelay`) and no restriction on `op.endpoint`, `op.callData`, or the transaction's `stack.signerAddress`. Because the post-loop accounting in `runAction` only tracks ERC20/ETH balances listed in `circomData.erc20TokenAddresses`, any non-ERC20 asset (e.g., an ERC721 LP position) that ends up owned by the Emporium contract as a side effect of a legitimate op is invisible to the accounting and persists in the contract indefinitely, allowing any subsequent unrelated caller to drain it via a crafted CASE 2 call.

### Finding Description
Equality claimed to hold: `owner(victimTokenId)` after any subsequent, unrelated attacker `transact()`/`runAction()` call should still equal the victim's stealth address (or otherwise-intended custodian), i.e. no unrelated third party should be able to move an asset that a victim's op produced.

Trace:
1. A victim performs a CASE 2 op through `EmporiumUpgradeable.runAction` (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:102-113`) that mints/receives an ERC721 (e.g., a Uniswap-v3-style LP NFT) with the recipient set to `address(Emporium)`. Nothing in `runAction` forces or checks that ERC721 assets are swept out: the pre/post balance snapshots (`balancesBefore`/`balancesAfter`, lines 85-87, 122-124) and the `handleOut` sweep (lines 162-184) only iterate `circomData.erc20TokenAddresses`, which never contains ERC721 token IDs. The NFT is now permanently owned by the Emporium contract.
2. `verifyWallet` (lines 302-349) only validates an EIP-712 signature when `stack.signerAddress != address(0)`; if `stack.signerAddress == address(0)` it returns immediately after marking the message used, with no signature check at all. When `signerAddress == address(0)`, the `if (op.invokeWallet && stack.signerAddress != address(0))` condition (line 98) is always false, so every op unconditionally executes as CASE 2.
3. An attacker (unprivileged, using only their own UTXOs/proof) submits a `transact()` call whose `CircomData.externalActionData` decodes to an `EmporiumStack` with `signerAddress = address(0)` and one op: `endpoint = nftContract`, `callData = abi.encodeCall(IERC721.safeTransferFrom, (address(Emporium), attackerEOA, victimTokenId))`. This passes the selector blacklist (it isn't `callHinkalWallet`/`doSendToRelay`), and `op.endpoint.call(op.callData)` executes with `msg.sender == Emporium`. Since `Emporium` is the actual `ownerOf(victimTokenId)`, `ERC721.safeTransferFrom` succeeds trivially (owner-initiated transfer requires no approval).
4. Nothing in `HinkalHelper.performHinkalChecks`, `dimensionsCheck`, `rootHashExists`, the slippage/balance requires in `Hinkal.sol`, or the circuit's `inTotal + amountChanges === outTotal` constraint touches this NFT transfer, because the attacker's own `circomData.erc20TokenAddresses`/`amountChanges` are unrelated to `nftContract`/`victimTokenId` (they can be empty or reference a token with 0 change). The shielded-pool accounting is entirely orthogonal to the raw external call executed inside the ops loop.

Root cause: CASE 2 imposes no allow-list or ownership/recipient constraint on `op.endpoint`/`op.callData`, and the contract has no bookkeeping for non-ERC20 assets that a prior op may have caused it to receive/hold.

### Impact Explanation
Any asset that ends up owned by the shared `EmporiumUpgradeable` contract (notably ERC721 LP positions from CASE-2-driven external protocol interactions) can be stolen by any unrelated, unprivileged attacker in an independent, self-proved `transact()` call. This is direct theft of in-flight/custodied user funds (the victim's LP NFT position) by a party who was never authorized by the victim's signature, proof, or stealth address derivation — matching the Critical category ("direct theft of shielded or in-flight user funds"). The attack is fully repeatable against every NFT (or any other asset type not modeled by `erc20TokenAddresses`) that accumulates at the Emporium address.

### Likelihood Explanation
Preconditions: some prior legitimate Emporium CASE 2 interaction must leave a non-ERC20 asset (e.g., an LP NFT) owned by the Emporium contract — a realistic outcome whenever an external protocol's mint/receive function is called with `recipient = address(this)` (Emporium) rather than immediately forwarding to the user, since `runAction` has no generic sweep for non-tracked asset types. Attacker cost is minimal: they only need to generate a valid proof for their own (possibly zero-value) UTXOs and craft one CASE 2 op; `verifyWallet` imposes zero signature requirement when `signerAddress == address(0)`. The exploit is fully feasible with only unprivileged capabilities listed in the rules and is repeatable for every stranded NFT.

### Recommendation
Restrict CASE 2 stateless calls so `op.endpoint.call` cannot move assets owned/held by the Emporium contract to arbitrary recipients without authorization tied to the acting signer/prover: e.g., require `stack.signerAddress != address(0)` with a verified signature for all ops (remove the no-signature bypass), maintain an explicit inventory/allow-list of non-ERC20 assets the Emporium is permitted to hold and require they be swept to the correct stealth address within the same `runAction` call (similar to the ERC20 balance-diff sweep), and/or restrict `op.endpoint` calls that transfer assets (`transferFrom`/`safeTransferFrom` and similar selectors) to only affect assets that were produced within the same transaction and are being routed to `circomData.stealthAddressStructure`'s derived recipient.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable` (or its proxy), a mock ERC721 with `mint(address to, uint256 id)`, and configure Hinkal/Emporium wiring per existing deployment helpers.
2. Victim step: build a `CircomData`/`EmporiumStack` with `signerAddress = address(0)` and a CASE 2 op calling `mockNFT.mint(address(Emporium), victimTokenId)` (or a mock LP `mint` that sets recipient to Emporium), submit via `transact()` with a valid Groth16 proof for the victim's own (dummy) UTXOs; assert `mockNFT.ownerOf(victimTokenId) == address(Emporium)` after this call.
3. Attacker step: build a second, independent `CircomData`/`EmporiumStack` with `signerAddress = address(0)` and a CASE 2 op = `abi.encodeCall(IERC721.safeTransferFrom, (address(Emporium), attackerEOA, victimTokenId))` on `mockNFT`, `erc20TokenAddresses` empty or unrelated, submit via `transact()` with the attacker's own valid proof.
4. Assert `mockNFT.ownerOf(victimTokenId) == attackerEOA` after step 3, proving `owner(victimTokenId)` transitioned from `Emporium` to the attacker's EOA without any authorization from the victim's stealth address/signature, breaking the claimed equality. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L97-118)
```text
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
