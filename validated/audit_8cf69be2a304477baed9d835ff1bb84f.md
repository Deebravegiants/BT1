### Title
Emporium's balance-scan only tracks ERC-20/ETH, letting an attacker sweep any NFT/ERC1155 stranded at the Emporium contract via an unrelated CASE 2 call - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction`'s before/after balance scan only iterates `circomData.erc20TokenAddresses` and only reads balances through `getERC20OrETHBalance`, which understands ERC-20/ETH exclusively. Any ERC721/ERC1155 asset that lands on the Emporium contract via a stateless (CASE 2) operation is invisible to this accounting, is never converted into a UTXO for its depositor, and can subsequently be pulled out by any unrelated, unprivileged caller through a second, totally unrelated `transact` call whose CASE 2 op simply calls `safeTransferFrom(Emporium, attacker, tokenId)`.

### Finding Description
The claimed equality is: *every asset that ends up at Emporium as a result of a user's op is represented by a UTXO owned by that user (or refunded to them), and no unrelated caller can move it.* This is violated because:

1. `runAction` computes `balancesBefore`/`balancesAfter` strictly over `circomData.erc20TokenAddresses`, using `getBalancesForArray` → `getERC20OrETHBalance`, which only calls `IERC20.balanceOf`/native balance [1](#0-0) [2](#0-1) . Nothing in this loop, or anywhere else in `runAction`, observes ERC721/ERC1155 ownership.
2. CASE 2 ("Stateless Interaction") lets any caller with a valid proof for their own funds embed an arbitrary `op.endpoint.call{value: op.value}(op.callData)` from the Emporium contract itself, the only restriction being that the selector isn't `callHinkalWallet`/`doSendToRelay` [3](#0-2) .
3. `verifyWallet` only checks a signature when `stack.signerAddress != address(0)`; when it's `address(0)` it just marks `emporiumMessage` used and returns, no signature or authorization over the op contents is required in that path [4](#0-3) .
4. `circomData.calldataHash` (which does bind `externalActionData`, including the encoded `EmporiumStack`) is only checked for integrity against the attacker's *own* proof/inputs in `performHinkalChecks` [5](#0-4) ; it does not constrain the op's `endpoint`/`callData` to any legitimate, pre-approved action - the attacker is free to encode any op they like as long as their own proof (over their own nullifiers/UTXOs) verifies.

Exploit flow: (a) a victim performs a CASE 2 op through Emporium that results in an NFT (`victimTokenId`) being transferred to the Emporium contract - e.g., the victim's op mints or receives the NFT to `address(Emporium)`, believing/expecting Hinkal to track it; because the `erc20TokenAddresses` array only lists ERC-20 tokens, this NFT movement is entirely outside the before/after balance diff, so `handleOut` never creates a UTXO for it, and it is not returned to the victim. (b) The NFT now sits at the Emporium contract indefinitely, unaccounted by any UTXO. (c) An unprivileged attacker later calls `Hinkal.transact` with their own valid proof (their own nullifiers/UTXOs, own `erc20TokenAddresses` — possibly empty), and a `circomData.externalActionData` targeting the Emporium action id, with `externalActionMetadata` encoding an `EmporiumStack` containing one op: `signerAddress = address(0)`, `invokeWallet = false`, `endpoint = <NFT contract>`, `callData = abi.encodeWithSelector(IERC721.safeTransferFrom.selector, Emporium, attacker, victimTokenId)`. In CASE 2 this call executes as `Emporium.call` against the NFT contract, so `msg.sender` inside the NFT contract is Emporium itself — the actual owner of `victimTokenId` — so the transfer succeeds without any approval. Nothing in the surrounding balance loop notices or blocks this because the NFT contract is never in the attacker's `erc20TokenAddresses` array (or, even if it were, `balanceOf` on an ERC721 happens to share the ERC20 selector but the amount semantics and slippage/UTXO logic are not designed for that and don't gate this call).

This is a distinct call from any legitimate op the victim signed/authorized, showing that `verifyWallet`, `performHinkalChecks`, and the balance-diff loop do not, together, prevent an unrelated party from directing Emporium to move an asset it holds that was never turned into a tracked UTXO.

### Impact Explanation
Any NFT (or ERC1155 token id) that ends up owned by the Emporium contract - whether from a victim's stateless op, an airdrop, or any other route - is (1) never represented as a spendable UTXO for its depositor (permanent freezing/loss from the depositor's perspective) and (2) trivially stealable by any unrelated, unprivileged caller via a single CASE 2 op in a completely unrelated `transact` call, with zero effect on their own `balanceDif`/UTXO/slippage equations. This is repeatable for every NFT/ERC1155 that ever lands at the Emporium address and costs the attacker only their own transaction gas plus a self-owned valid proof.

### Likelihood Explanation
Precondition: an ERC721/ERC1155 token must be sitting at the Emporium contract address (via any victim CASE 2 op, or otherwise). Given that, the attack requires no special role, no interaction with the victim, and no bypass of any check that currently exists for ERC-20/ETH accounting, since that accounting simply does not apply to non-ERC20 tokens. The attacker only needs the ability to deploy contracts and craft `CircomData`/`EmporiumStack`, which are explicitly in-scope attacker capabilities.

### Recommendation
Extend Emporium's (and any other CASE-2-capable external action's) post-op accounting to also enumerate and gate ERC721/ERC1155 transfers - e.g., require any op whose target/selector matches `IERC721`/`IERC1155` transfer functions to be explicitly declared in `circomData` and produce a corresponding UTXO/refund path, or disallow CASE 2 ops from calling arbitrary `safeTransferFrom`/`transferFrom` selectors on tokens not enumerated and constrained by the circuit. At minimum, before allowing unconstrained low-level calls in CASE 2, restrict `op.endpoint` to an allow-list of known-safe DeFi routers/tokens, and always keep NFTs custodied by a component that requires the same nullifier-based authorization applied to ERC-20 balances.

### Proof of Concept
1. Deploy `Hinkal`, `EmporiumUpgradeable`, and a mock `ERC721`.
2. As "victim", perform a `transact` call with `externalActionData` targeting Emporium, with one CASE 2 op that mints/transfers `tokenId` to `address(Emporium)`; assert `Emporium` is now `ownerOf(tokenId)`, and assert no `UTXO`/commitment event was emitted referencing that token (the returned `utxoSet` length for that call only reflects ERC-20 entries).
3. As "attacker" (a different EOA, with their own arbitrary valid UTXO/proof, unrelated to the victim), perform a second, unrelated `transact` call whose CASE 2 op is `abi.encodeWithSelector(IERC721.safeTransferFrom.selector, Emporium, attacker, tokenId)` targeting the NFT contract as `endpoint`.
4. Assert the call succeeds, `ownerOf(tokenId) == attacker`, and assert that the attacker's own `balanceDif`/`deltaAmountChanges`/slippage equations for their own ERC-20 tokens were unaffected (i.e., the theft happened with zero recorded impact on the balance equation). [6](#0-5) [2](#0-1)

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-316)
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
