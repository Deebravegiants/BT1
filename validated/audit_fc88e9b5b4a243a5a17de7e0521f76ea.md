This confirms the mechanics: `EmporiumOperation.invokeWallet` is fully attacker-controlled (set `false` to force CASE 2), and CASE 2 executes an unrestricted `op.endpoint.call{value: op.value}(op.callData)` from the Emporium contract's own address, gated only against two specific `IHinkalWallet` selectors.

### Title
Arbitrary low-level call in `EmporiumUpgradeable.runAction` CASE-2 lets any caller drain NFTs/assets left at the Emporium contract - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction`'s stateless-operation branch performs `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract's own address, with the only restriction being a blocklist of two `IHinkalWallet` selectors. Because `circomData.erc20TokenAddresses` (the only asset set checked by `getBalancesForArray`/the balance-diff invariant in `Hinkal.transact`) is fully attacker-chosen and need not include an NFT contract, an attacker can invoke `runAction` with their own valid proof and use a CASE-2 op to call `safeTransferFrom(Emporium, attacker, tokenId)` on any ERC721 the Emporium contract happens to hold, with no check that the token or its owner has any relationship to the attacker's own circomData/signer.

### Finding Description
Equality claimed broken: `owner(tokenId) after a user's op == that user's stealth address/wallet`. Trace:

- `Transferer.onERC721Received`/`onERC1155Received` accept any incoming transfer unconditionally and record no state binding the tokenId to any signer [1](#0-0) .
- `EmporiumUpgradeable.runAction` decodes an attacker-supplied `EmporiumStack` from `circomData.externalActionData.externalActionMetadata` and loops over `stack.ops`. For each op, if `op.invokeWallet && stack.signerAddress != address(0)` it goes through the wallet (CASE 1); otherwise (CASE 2) it does a raw call `op.endpoint.call{value: op.value}(op.callData)` executed with `msg.sender == address(Emporium)`, blocking only `callHinkalWallet`/`doSendToRelay` selectors [2](#0-1) .
- `EmporiumOperation.invokeWallet`, `endpoint`, and `callData` are entirely attacker-supplied fields inside the abi-encoded `EmporiumStack` [3](#0-2) .
- The only pre/post-state check in `runAction` is `getBalancesForArray(circomData.erc20TokenAddresses)` (fungible ERC20/ETH balances of tokens the caller lists themselves) plus `BalanceChangeShouldBePositive`; there is no tracking of NFT ownership at all [4](#0-3)  and [5](#0-4) .
- `runAction` is gated by `onlyAllowedRecipient`, which only checks `msg.sender` is an allow-listed caller (i.e., `Hinkal`), not that the op targets/assets belong to the calling proof's signer [6](#0-5) .
- Upstream, `Hinkal.transact` -> `_externalTransact` -> `IExternalActionV2(...).runAction` reaches this with any attacker-chosen `circomData`, as long as the attacker supplies a valid Groth16 proof for their own UTXO nullifiers; `circomData.erc20TokenAddresses` and its slippage/balance-diff checks in `Hinkal.transact` are scoped only to the tokens the attacker lists, so an NFT contract never appears there and is never checked [7](#0-6) .

Root cause: the Emporium contract's CASE-2 "stateless op" is an unrestricted arbitrary-call primitive executed as `address(Emporium)`, and no code anywhere binds an incoming NFT/asset held by Emporium to the specific op-signer/stealth address that produced it. If any victim op leaves an NFT (or any asset not enumerated in a later `erc20TokenAddresses` list, e.g., a multi-step claim/mint flow that temporarily lands the NFT at Emporium) owned by the Emporium contract, any other unprivileged party can, in an unrelated transaction with only their own valid proof, submit a CASE-2 op that calls `safeTransferFrom(Emporium, attacker, tokenId)` and steal it. None of `performHinkalChecks`, `dimensionsCheck`, `checkOnchainCreation`, `verifyProof`, `rootHashExists`, or the ERC20/ETH balance-diff invariant in `Hinkal.transact` constrain the NFT/asset, because they only operate over the caller-supplied `erc20TokenAddresses` array and circuit-verified fungible amounts — none of which need reference the stolen NFT.

### Impact Explanation
Critical — direct theft of a shielded-created, non-fungible (or any un-enumerated) asset belonging to another user, with no proof/nullifier check tying it to the thief. Repeatable against every NFT/asset that transiently or persistently sits at the Emporium contract's address, at negligible attacker cost (their own valid, possibly zero-value, proof plus the crafted `EmporiumStack`).

### Likelihood Explanation
Requires only that some NFT/asset be owned by `address(Emporium)` at the time of the attack (a realistic state whenever an Emporium op's operation sequence mints/claims/receives an NFT to `address(this)` mid-flow, e.g. across a multi-op claim pattern, or any op that doesn't itself forward the NFT out in the same atomic call). The attacker needs no special role — any EOA that can deposit into Hinkal and generate a proof for their own UTXO can craft the `EmporiumStack`/`EmporiumOperation` and call `Hinkal.transact` targeting `EmporiumUpgradeable`.

### Recommendation
Do not allow CASE-2 stateless ops to make arbitrary calls from the Emporium contract's own address to arbitrary endpoints holding third-party assets. Either (a) require every op-callData that transfers an NFT/ERC721/ERC1155/undeclared asset out of Emporium to be authorized by a signature/commitment tied to the specific owning signer (similar to `verifyWallet`'s EIP-712 check, but covering NFTs, not just fungible-token relay fees), or (b) never let assets sit owned by `address(Emporium)` across transaction boundaries — require every op sequence that receives an NFT to forward it to the destination stealth address/wallet within the same atomic `runAction` call, and add an allowlist/registry restricting which `op.endpoint`/selectors are callable in CASE 2.

### Proof of Concept
Foundry fork test:
1. Deploy a mock ERC721 with a `claim(address to, uint256 tokenId)` function that mints to `msg.sender`.
2. As the victim, call `Hinkal.transact` with a valid proof and an `EmporiumStack` whose single CASE-2 op calls `mockNft.claim(address(Emporium), tokenId)` (simulating a claim flow that lands the NFT at Emporium mid-flow, e.g. because a later forwarding op in the same stack is omitted/fails in a separate tx). Assert `mockNft.ownerOf(tokenId) == address(Emporium)`.
3. As the attacker (unrelated EOA with their own deposited UTXO and valid proof), call `Hinkal.transact` targeting `EmporiumUpgradeable.runAction` with a `circomData.erc20TokenAddresses` that omits the NFT, and an `EmporiumStack` whose CASE-2 op calls `mockNft.safeTransferFrom(address(Emporium), attacker, tokenId)`.
4. Assert `mockNft.ownerOf(tokenId) == attacker` and that the victim's original commitment/nullifier state is unaffected (no nullifier was ever spent by the attacker's tx corresponding to the victim's NFT UTXO), proving direct theft.

### Citations

**File:** contracts/Transferer.sol (L19-36)
```text
    function onERC721Received(
        address,
        address,
        uint256,
        bytes calldata
    ) public pure returns (bytes4) {
        return IERC721Receiver.onERC721Received.selector;
    }

    function onERC1155Received(
        address,
        address,
        uint256,
        uint256,
        bytes calldata
    ) public pure returns (bytes4) {
        return IERC1155Receiver.onERC1155Received.selector;
    }
```

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-144)
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
```

**File:** contracts/external-actions/emporium/EmporiumStack.sol (L4-19)
```text
struct EmporiumOperation {
    address endpoint;
    bool invokeWallet;
    uint128 value;
    bytes callData;
}

struct EmporiumStack {
    uint8 v;
    bytes32 r;
    bytes32 s;
    address signerAddress;
    EmporiumOperation[] ops;
    uint256 maxFee;
    uint256 deadline;
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
