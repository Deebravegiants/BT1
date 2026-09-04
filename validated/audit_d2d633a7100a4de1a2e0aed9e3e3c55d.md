### Title
Arbitrary unauthenticated calls from `EmporiumUpgradeable` in "stateless" mode allow anyone to drain any asset stranded on the Emporium contract - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` supports a "Case 2: Stateless Interaction" branch that executes `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract whenever `stack.signerAddress == address(0)`. In that same branch, `verifyWallet` skips ECDSA signature verification entirely for `signerAddress == address(0)`, so the only requirement to run an operation is a fresh `emporiumMessage` nonce, which any caller can freely choose. Combined with the fact that Emporium's post-call accounting (`getBalancesForArray`) only tracks the ERC20 addresses listed in `circomData.erc20TokenAddresses`, this mirrors the Magnetar `MagnetarAction.OFT`/`MagnetarAction.Permit` pattern from the referenced report: any asset that ends up owned by the shared "proxy" contract (via a mint, an approval, or any other side effect not reflected in the tracked ERC20 balance array) is retrievable by any unrelated caller, because the call itself is unauthenticated and unrestricted in target/calldata.

### Finding Description
`EmporiumUpgradeable.runAction` (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:76-160`) decodes an `EmporiumStack` from `circomData.externalActionData.externalActionMetadata` and, for each `EmporiumOperation`, either:
- routes the call through the user's `HinkalWallet` (`invokeWallet == true && signerAddress != 0`), which is EIP-712 signed and access-controlled by `onlyEmporium`, or
- executes the call directly as the Emporium contract itself when `invokeWallet` is false or `signerAddress == address(0)`: [1](#0-0) 

`verifyWallet` only enforces the EIP-712 signature check (binding `endpoint`, `invokeWallet`, `value`, `callData` to a signer) when `stack.signerAddress != address(0)`; if it is `address(0)` it returns immediately after marking the nonce used: [2](#0-1) 

The only restriction on the "stateless" call is that the calldata selector isn't `callHinkalWallet`/`doSendToRelay` on the wallet interface — there is no restriction on `op.endpoint` or the rest of `op.callData`: [3](#0-2) 

Post-call, Emporium only measures balance deltas for the ERC20 tokens explicitly listed in `circomData.erc20TokenAddresses` and forwards any positive delta to `msg.sender` (the caller of `runAction`, i.e., Hinkal on behalf of whoever submitted the transaction): [4](#0-3) 

This reproduces the exact bug class from the Magnetar report: (1) if any external protocol call performed through Emporium mints or leaves behind an asset not in `erc20TokenAddresses` (e.g., an ERC721/ERC1155 position, or a dust ERC20 balance from a partially-failed multi-hop op, or a lingering `approve` to a third party), it is not accounted for or returned to the depositor and instead sits owned by/approved to the Emporium contract; and (2) because the "stateless" branch lets an unrelated, unauthenticated actor perform an arbitrary `endpoint.call(callData)` originating from Emporium (limited only by ERC20 delta accounting, which does not cover NFTs, approvals, or other assets), that stranded asset can later be swept out by anyone via a call such as `IERC721(nft).transferFrom(emporium, attacker, tokenId)` or `IERC20(token).transfer(attacker, amount)`, exactly as `MagnetarAction.OFT`/`Permit` allowed sweeping stuck/approved tokens out of `Magnetar`.

The equality broken is the same balance-conservation invariant Emporium is supposed to guarantee: total value that entered Emporium via `_externalTransact`'s pre-transfer plus what the op sequence produces should equal what is returned to the legitimate depositor via `handleOut`/UTXO issuance. Because tracked accounting is scoped only to the token list supplied by the *caller* of the current transaction, and the outbound call is otherwise unauthenticated when `signerAddress == 0`, an attacker who supplies a token list that excludes the stranded asset (or targets an asset type Emporium never tracks) can extract value that was never part of their own deposit.

### Impact Explanation
This allows theft of assets that legitimately belong to another user but happen to be temporarily or erroneously held by the shared `EmporiumUpgradeable` contract (positions minted to it, dust left after partial multi-step DeFi interactions, or approvals granted to third-party protocols during a swap/lend operation that are never revoked). This matches "temporary/permanent freezing of user funds" turning into "theft or unauthorised asset movement" per the impact criteria, since the Emporium contract's own balance/approvals are moved by a caller who never contributed that value and was never authorised by the true depositor's signature (the stateless path explicitly bypasses the EIP-712 signer check).

### Likelihood Explanation
Likelihood is comparable to the original finding: it requires (a) some prior interaction through Emporium leaving an asset behind that is outside the ERC20-delta accounting (a real possibility any time `op.endpoint.call` is used to interact with a protocol that mints NFTs/receipts, leaves dust, or grants allowances), and (b) an attacker/advanced user to notice the stranded value and submit a follow-up `transact()` call through Hinkal targeting Emporium with `signerAddress == address(0)` and a crafted `EmporiumOperation`. Both steps are permissionless and require no privileged role, matching the "advanced user, unprivileged EOA" threat model of the referenced report.

### Recommendation
- Restrict the "stateless" `op.endpoint.call` path so it can only target a pre-approved allowlist of protocol contracts (not arbitrary addresses), and/or require that `signerAddress != address(0)` (i.e., always go through a per-user `HinkalWallet`) so every external call is bound to a specific EIP-712-signed intent.
- Extend Emporium's before/after accounting to cover ERC721/ERC1155 balances (or any asset class the allowed ops can produce), not just the caller-supplied ERC20 list, and revert if any tracked or untracked asset balance increased without being returned to the legitimate depositor in the same transaction.
- Ensure any allowance granted by Emporium/HinkalWallet to a third-party protocol during an operation is reset to zero at the end of `runAction`, so stray approvals cannot be exploited by a later unrelated caller.

### Proof of Concept
Conceptual sequence (mirrors the Magnetar PoC pattern):
1. A user performs a legitimate `transact()` through Hinkal, routing an `EmporiumOperation` to some external protocol (e.g., an options/staking contract) that mints a receipt NFT to `msg.sender`. Since the call executes with Emporium as `msg.sender`, the NFT is minted to `EmporiumUpgradeable`'s address and is not tracked by `getBalancesForArray` (ERC20-only).
2. The user's `transact()` completes successfully; the NFT remains stuck on the Emporium contract, unreachable by the user themselves through normal Emporium flows.
3. An unrelated attacker submits their own `transact()` call through Hinkal (using a trivial/self-owned proof), with `externalActionData.externalActionAddress = Emporium`, and `externalActionMetadata` encoding an `EmporiumStack` with `signerAddress = address(0)` and a single op: `{ endpoint: nftContract, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC721.transferFrom.selector, emporiumAddress, attacker, tokenId) }`.
4. `verifyWallet` passes trivially (no signature required when `signerAddress == 0`), the selector isn't `callHinkalWallet`/`doSendToRelay`, so `runAction` executes `nftContract.transferFrom(emporium, attacker, tokenId)` directly, transferring the victim's stranded NFT to the attacker.

Note: I was not able to inspect `circuits/MainEVMCircuit.circom` in enough depth in this pass to confirm the exact mechanics by which an attacker's own valid Groth16 proof (with zero/self-owned UTXOs) can carry arbitrary `externalActionMetadata` bound via `calldataHash`; this is a reasonable assumption given the public, permissionless nature of proof generation in this architecture, but should be verified against the circuit's public-input constraints before treating this as fully confirmed.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-317)
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
