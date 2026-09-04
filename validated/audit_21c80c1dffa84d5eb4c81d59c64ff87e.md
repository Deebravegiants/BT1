### Title
Emporium `runAction` never tracks or reconciles non-listed assets (e.g. LP NFTs) acquired by the Emporium contract, and `verifyWallet` allows any un-signed `EmporiumOperation` (`signerAddress == address(0)`) to move them out - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` only diffs and reconciles balances for the tokens explicitly listed in `circomData.erc20TokenAddresses`; any other asset the executed `EmporiumOperation` calls acquire (e.g. a Uniswap-V3-style LP NFT minted to `address(this)`) is left permanently owned by the shared Emporium contract with no corresponding UTXO. Because `verifyWallet` skips all signature checks whenever `stack.signerAddress == address(0)`, any unrelated, unprivileged actor who can pass Hinkal's normal proof checks for their own trivial UTXO can submit a fresh `EmporiumStack` whose `EmporiumOperation.callData` calls `positionManager.transferFrom(emporium, attacker, tokenId)`, executed with `msg.sender == emporium` (the NFT's owner), and steal the asset.

### Finding Description
The broken equality: for every asset actually acted on by `op.callData` inside the loop at [1](#0-0) , there is **no** equality enforced against `circomData.erc20TokenAddresses` (the only assets whose custody is tracked and reconciled into UTXOs bound to `circomData.stealthAddressStructure.stealthAddress`). The reconciliation loop at [2](#0-1)  iterates only `circomData.erc20TokenAddresses.length` entries, calling `getBalancesForArray`/`handleOut` only for those tokens [3](#0-2) [4](#0-3) . Any asset an `op.endpoint.call` acquires that is not in this array (an ERC-721 LP position minted with `recipient` defaulting to `msg.sender == emporium`) never enters `balancesBefore`/`balancesAfter`, never produces a `UTXO`, and is simply left owned by the Emporium contract with no shielded record.

Root cause #2 - the withdrawal path requires no authorization from anyone: `verifyWallet` only enforces the EIP-712 signature check and `maxFee`/`deadline` bounds when `stack.signerAddress != address(0)`; if `signerAddress == address(0)` it returns immediately after marking `emporiumMessage` used [5](#0-4) . In CASE 2 ("Stateless Interaction"), `op.endpoint.call{value: op.value}(op.callData)` executes with `msg.sender == address(emporium)` [6](#0-5) , and `onlyAllowedRecipient` only checks that the *caller of `runAction`* (i.e. Hinkal itself) is whitelisted [7](#0-6)  — it places no constraint on which `endpoint`/`callData` a given prover may submit, nor does it bind the ops to the depositor who owns the asset being acted upon.

Exploit flow:
1. Victim's `EmporiumOperation` calls a Uniswap-V3-style `NonfungiblePositionManager.mint(...)` (recipient omitted/defaulted), so the LP NFT is minted to `msg.sender == emporium`. `circomData.erc20TokenAddresses` lists only the 2 ERC20s consumed, satisfying `dimensionsCheck`'s `tokenCount` requirement. No UTXO for the NFT is ever created.
2. Any later unprivileged attacker (who only needs their own trivial deposit/UTXO to satisfy Hinkal's proof checks and produce a valid Groth16 proof for a `runAction` call with `externalActionId` = Emporium) crafts a fresh `EmporiumStack` with `signerAddress = address(0)` and a single op: `endpoint = positionManager`, `callData = transferFrom(emporium, attacker, tokenId)`. `circomData.erc20TokenAddresses` for this call need not reference the NFT/position manager at all — it can be any unrelated token(s) matching `dimensions.tokenNumber`.
3. `verifyWallet` performs no signature check (signerAddress is zero) and just consumes a fresh `emporiumMessage`. The call executes `positionManager.transferFrom(emporium, attacker, tokenId)` with `msg.sender == emporium`, which is the NFT owner, so ERC-721's owner/approval check passes trivially.
4. The NFT leaves the Emporium contract to the attacker. The `balancesAfter`/`balancesBefore` reconciliation for the erc20TokenAddresses supplied in this second transaction never observes or blocks this, because the NFT contract/tokenId is outside that array's scope.

Existing guards do not prevent this: `performHinkalChecks`/`dimensionsCheck` only validate array-length consistency between `circomData` fields and `Dimensions`, they never constrain which contracts an `EmporiumOperation.endpoint`/`callData` may target, nor do they tie the executed calls' side effects to `circomData.erc20TokenAddresses`. The circuit's `inTotal + amountChanges === outTotal` constraint only balances the declared ERC20/ETH amounts and has no signal representing arbitrary external-call side effects like NFT transfers. `rootHashExists`, `nullifiers`/`usedMessages` replay protection, and `nonReentrant` are all satisfied normally by both transactions and do not detect the mismatch.

### Impact Explanation
Any value (ERC-721 LP position, or in general any asset type not listed in `erc20TokenAddresses`) that ends up custodied by the shared `EmporiumUpgradeable` contract as a side effect of one user's `EmporiumOperation` can be permanently and unilaterally extracted by any other unrelated, unprivileged actor, because `verifyWallet` imposes zero authorization when `signerAddress == address(0)`. This is a direct theft of another user's asset held by the protocol's shared contract — Critical severity, matching "direct theft of shielded or in-flight user funds ... executing calls or moving assets a wallet owner or prover never authorised." It is repeatable for every victim `EmporiumOperation` that causes the Emporium contract to acquire an asset outside the declared `erc20TokenAddresses` set (LP NFTs, other ERC-721/1155 tokens, staking receipt tokens, etc.).

### Likelihood Explanation
Preconditions are attacker-achievable with only unprivileged capabilities: the attacker needs their own funded UTXO/deposit (even dust) to pass Hinkal's normal proof/deposit checks, the ability to craft `circomData`/`Dimensions`/`externalActionMetadata` for the Emporium action, and knowledge of the victim's LP `tokenId` (public on-chain data once the victim's mint transaction is observed). No relayer collusion, no privileged role, and no signature forgery are required, since `signerAddress = address(0)` deliberately skips the signature path. This is realistically exploitable by any actor who monitors Emporium transactions and reacts once an asset outside the declared token set becomes emporium-owned.

### Recommendation
Require `EmporiumOperation` execution to be constrained to assets declared in `circomData.erc20TokenAddresses`/reconciled UTXOs, e.g. by: (a) disallowing stateless (`signerAddress == 0`) `EmporiumOperation`s from targeting arbitrary `endpoint`s that are not on a per-user allowlist bound to the originating deposit/prover, (b) requiring `verifyWallet` to always validate a signature/authorization tied to the beneficial owner of any asset the ops interact with (not skip entirely when `signerAddress == 0`), and/or (c) extending the balance-reconciliation loop to detect and revert on any externally observable asset-ownership change (e.g. via `ERC721.ownerOf` diffing for a declared NFT allowlist) that isn't accounted for by `circomData.erc20TokenAddresses`/UTXO output, so no asset can silently accrue to the shared Emporium contract without becoming a provably-owned UTXO.

### Proof of Concept
Hardhat fork test plan:
1. Deploy `EmporiumUpgradeable`, `Hinkal`, `HinkalHelper`, a mock Uniswap-V3-style `NonfungiblePositionManager` (ERC-721), and two mock ERC20s.
2. Victim deposits/generates a valid Groth16 proof and calls `Hinkal.transact` with `externalActionId` = Emporium, `circomData.erc20TokenAddresses = [tokenA, tokenB]`, and `EmporiumStack.ops[0]` calling `positionManager.mint(...)` with default recipient (`msg.sender`). Assert `positionManager.ownerOf(tokenId) == address(emporium)` after the call, and assert the returned `utxoSet` only contains entries for `tokenA`/`tokenB` (no representation of `tokenId`).
3. Attacker (unrelated EOA) deposits a trivial amount, generates their own valid proof, and calls `Hinkal.transact` with a new `emporiumMessage`, `EmporiumStack.signerAddress = address(0)`, and `ops[0] = { endpoint: positionManager, callData: transferFrom(emporium, attacker, tokenId) }`; `circomData.erc20TokenAddresses` references only unrelated dummy tokens.
4. Assert the call succeeds and `positionManager.ownerOf(tokenId) == attacker`, proving theft of the victim's LP position with no equality ever enforced between `tokenId`/`positionManager` and `circomData.erc20TokenAddresses`/`stealthAddressStructure.stealthAddress`.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-87)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-118)
```text
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-124)
```text
        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-151)
```text
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
