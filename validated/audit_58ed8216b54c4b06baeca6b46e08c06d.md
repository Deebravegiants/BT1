### Title
Unauthenticated theft of Uniswap-V3-style LP positions custodied by `EmporiumUpgradeable` via stateless (CASE 2) operations - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction`'s stateless "CASE 2" branch executes `op.endpoint.call{value: op.value}(op.callData)` directly as the Emporium contract itself, with the only guard being `verifyWallet`, whose signature check is either skipped entirely (`stack.signerAddress == address(0)`) or, when present, only authenticates the caller's own op list - never the identity of whoever originally deposited an asset into Emporium's custody. Because any non-ERC20 asset left in Emporium (e.g. a Uniswap-V3-style position NFT from an earlier mint) is invisible to the balance-diffing accounting used to mint output UTXOs, ownership of that asset is effectively "whoever calls Emporium next," letting any unprivileged attacker redirect `collect`/`decreaseLiquidity` proceeds to themselves.

### Finding Description
The claimed broken equality: **`beneficiary_of_LP_position == original_depositor_of_LP_position`** should always hold; the exploit breaks it to **`beneficiary_of_LP_position == msg.sender_of_latest_Emporium_tx`**.

Code path:
- `runAction` decodes attacker-controlled `EmporiumStack` from `circomData.externalActionData.externalActionMetadata` [1](#0-0) .
- `verifyWallet` is called before any op executes. If `stack.signerAddress == address(0)`, it marks the message used and returns immediately - no EIP-712 signature, no binding to any depositor at all [2](#0-1) .
- Even when `signerAddress != address(0)` and a valid signature is supplied, that signature only proves the *caller* authorized *their own* op list (`EMPORIUM_SIGNATURE_TYPEHASH` over `ops`, `maxFee`, `deadline`) [3](#0-2) . Nothing in this scheme ties a specific external asset (e.g. a Uniswap NFT `tokenId`) held by Emporium to the wallet/stealth address that originally deposited it.
- In the "CASE 2: Stateless Interaction" branch, the call is executed directly `op.endpoint.call{value: op.value}(op.callData)` from `address(this)` (Emporium), the only restriction being a block on `callHinkalWallet`/`doSendToRelay` selectors - any other endpoint/selector is allowed [4](#0-3) .
- The only value-tracking mechanism in `runAction` is ERC20/ETH balance diffing over `circomData.erc20TokenAddresses` (`balancesBefore`/`balancesAfter`) used to mint out-UTXOs [5](#0-4) . A Uniswap V3 position NFT minted with `recipient = emporium` is never captured by this loop; it just sits owned by the shared Emporium contract with no on-chain record of which depositor is entitled to it.

Exploit flow:
1. Victim performs a legitimate Emporium CASE 2 transaction whose `op.callData` calls `NonfungiblePositionManager.mint(...)` with `recipient = emporium`, funded by their own deposited UTXOs (balance-diff accounting is satisfied normally). The resulting `tokenId` is now owned by the Emporium contract address, and this state persists across transactions.
2. Attacker (unprivileged, own UTXOs only) submits a second, unrelated Emporium CASE 2 transaction with `EmporiumStack{signerAddress: address(0), ops: [op]}` where `op.callData` encodes `NonfungiblePositionManager.decreaseLiquidity(tokenId, ...)` followed by `collect({tokenId, recipient: attacker, amount0Max: max, amount1Max: max})`.
3. Because `msg.sender` for that call is Emporium (the NFT's owner as recognized by the position manager), Uniswap's `onlyApprovedOrOwner` check passes trivially - Emporium's own custody is misused as authorization.
4. `collect`'s `recipient` field sends the underlying principal + accrued fees directly to the attacker's address, bypassing Emporium's balance-diff loop entirely (since tokens never touch Emporium's own balance), so no nullifier, UTXO, or fee-payment logic is even triggered for the stolen value.

Existing guards fail to prevent this because: `verifyWallet` only authenticates the caller's own op list (or nothing, when `signerAddress == address(0)`) and has no concept of asset-to-depositor binding; `onlyAllowedRecipient` only restricts who may call `runAction` (a whitelisted relay/helper contract), not what `op.endpoint`/`op.callData` may target; the balance-diff/out-UTXO accounting only covers `circomData.erc20TokenAddresses`, never NFTs or other externally-tracked resources left in Emporium's custody.

### Impact Explanation
Critical - direct theft of a victim's shielded/deposited value (LP principal plus accrued, unclaimed trading fees) that was custodied by the shared `EmporiumUpgradeable` contract, with zero corresponding nullifier spend or signature from the true depositor. Any user (not just the original depositor) can drain any Uniswap-V3-style position - or any other stateful/non-ERC20 asset - that ends up owned by Emporium via a stateless mint/deposit, as many times as such positions exist, at zero cost beyond gas.

### Likelihood Explanation
Requires only that some prior Emporium transaction mint/deposit an NFT-based (or otherwise non-ERC20-tracked) position with `recipient = emporium`, which is a normal/expected usage pattern for the stateless CASE 2 mechanism (e.g., building LP positions without needing a per-user `HinkalWallet`). The attacker needs only knowledge of the resulting `tokenId` (discoverable from on-chain mint events) and the ability to submit their own Emporium transaction - no privileged role, no victim key material, no signature forgery required.

### Recommendation
Do not let stateless CASE 2 calls leave persistent, asset-bearing state (e.g., NFT ownership) in the shared Emporium contract across transactions. Either (a) require CASE 2 external calls that create custodial positions to immediately transfer the resulting asset out to the depositor's stealth address/wallet within the same transaction, mirroring the ERC20 balance-diff pattern, or (b) if positions must be held long-term by Emporium, add an explicit per-`tokenId` (or per-resource) ownership registry mapping each custodied asset to the depositor's committed identity/stealth address, and enforce that only a proof/signature binding to that identity can act on `decreaseLiquidity`/`collect`/similar calls for that specific asset.

### Proof of Concept
Hardhat fork test plan:
1. Deploy `EmporiumUpgradeable`, `HinkalWallet`, and a mock Uniswap-V3-like `NonfungiblePositionManager` (mint/decreaseLiquidity/collect) with an underlying pool holding two mock ERC20 tokens.
2. Victim: submit an Emporium CASE 2 `runAction` call (`stack.signerAddress = address(0)`) whose `op.callData` is `mint({..., recipient: emporium})`; assert `nftManager.ownerOf(tokenId) == emporium`.
3. Attacker (different EOA, unrelated deposit/nullifier): submit a second Emporium CASE 2 `runAction` call with `stack.signerAddress = address(0)`, `op.callData` = `decreaseLiquidity(tokenId, liquidity, 0, 0, deadline)` followed by `collect({tokenId, recipient: attacker, amount0Max: type(uint128).max, amount1Max: type(uint128).max})`.
4. Assert: attacker's ERC20 balances increase by the full principal + fees of the position; `emporium`'s tracked balances (`balancesBefore`/`balancesAfter` diff for `circomData.erc20TokenAddresses`) show no corresponding decrease requiring a nullifier spend; no `UsedMessage`/`InvalidSignature` revert occurs despite `signerAddress == address(0)`.
5. Equality check: assert `attacker_balance_after - attacker_balance_before == victim's original principal + accrued fees` while `victim_nullifiers_spent_for_this_amount == 0`, demonstrating the broken equality between rightful beneficiary and actual recipient.

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-151)
```text
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L284-348)
```text
    function _hashEmporiumOps(
        EmporiumOperation[] memory ops
    ) private pure returns (bytes32) {
        bytes32[] memory opHashes = new bytes32[](ops.length);
        for (uint256 i = 0; i < ops.length; i++) {
            opHashes[i] = keccak256(
                abi.encode(
                    EMPORIUM_OPERATION_TYPEHASH,
                    ops[i].endpoint,
                    ops[i].invokeWallet,
                    ops[i].value,
                    keccak256(ops[i].callData)
                )
            );
        }
        return keccak256(abi.encodePacked(opHashes));
    }

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
```
