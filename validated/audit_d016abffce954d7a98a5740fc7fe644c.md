### Title
Emporium `runAction` has no order/position ownership check, allowing any user to race-claim another user's settled limit-order proceeds - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` executes a fully attacker-supplied `EmporiumStack.ops` array with Emporium's own authority (`address(this)` as `msg.sender` for every call), and when `signerAddress == address(0)` the `verifyWallet` check performs **no validation of the ops content at all** — only a nonce (`emporiumMessage`) uniqueness check. Any unprivileged user can therefore submit their own valid Hinkal proof carrying an `EmporiumStack` whose ops invoke a settlement/claim function (e.g. Uniswap V3 `collect()`, an order-book `claim()`) on a position that a *different* user's order created, and `handleOut` will mint the resulting balance delta as a shielded UTXO to the caller's own stealth address, not the order's original author.

### Finding Description
The claimed equality — "first successful withdrawal against a settled-order balance == the account whose proof originated the order (victim)" — is **not enforced anywhere** in this contract. `runAction` is gated only by `onlyAllowedRecipient` [1](#0-0) , which checks that `msg.sender` (the calling Hinkal core contract) is whitelisted — it says nothing about which end user's proof triggered the call.

Inside `runAction`, the `EmporiumStack` is `abi.decode`d straight from `circomData.externalActionData.externalActionMetadata` [2](#0-1) . `verifyWallet` only enforces the EIP-712 `stack.signerAddress` signature check when `stack.signerAddress != address(0)`; when it is zero it returns immediately after marking the nonce used, performing zero validation of `stack.ops` [3](#0-2) . Nothing in `dimensionsCheck`, `checkOnchainCreation`, or `performHinkalChecks` in `HinkalHelper.sol` constrains `externalActionMetadata`'s content to belong to any particular order/position owner — it is only bound into `calldataHash` for the *caller's own* transaction integrity [4](#0-3) , not checked against any on-chain order registry.

The ops themselves are then executed as `address(this).call(...)` (Emporium itself as `msg.sender` in the low-level call) for both the stateless and stateful cases [5](#0-4) . Since Emporium is the shared, single on-chain identity/owner for *all* users' positions (e.g. it holds the Uniswap V3 NFT / is the maker on an order book), any external protocol call that is gated by "must be the position owner/maker" (Uniswap's `isAuthorizedForToken`, an order book's `msg.sender == maker`) is satisfied purely because Emporium itself is making the call — regardless of which end-user requested it.

`handleOut` distributes whatever positive `balancesAfter - balancesBefore` delta occurred *during that specific `runAction` call* to `msg.sender` (Hinkal core, which mints the shielded output to `circomData.stealthAddressStructure` — the **caller's own** key material) [6](#0-5) . So whoever's `runAction` invocation happens to trigger the actual settlement/claim transfer into Emporium (e.g. by including a `collect()`/`claim()` op) receives the UTXO, not the account that originally deposited/created the order.

Exploit flow: victim uses Emporium to place a Uniswap V3 range order / GTC order (Emporium becomes the maker/position owner). Attacker, from their own unprivileged EOA, supplies the opposing liquidity/fill entirely outside Hinkal, causing the order to become fillable/settled — but because Uniswap V3 (and most order books) require an explicit claim/collect step to actually move tokens to the maker, the proceeds are not yet in Emporium's spendable balance. Attacker then submits their own Hinkal `transact` call (their own valid ZK proof, own UTXOs, `deltaAmountChanges[i] == 0` for the settled token) with an `EmporiumStack` (`signerAddress == address(0)`, so no ops validation) whose ops call `collect()`/`claim()` against the victim's position. This runs before the victim's own claim transaction, so the resulting positive balance delta is captured and shielded to the attacker's stealth address via `handleOut`, stealing the victim's proceeds.

### Impact Explanation
Direct theft of shielded/in-flight user funds: another user's settled trade/order proceeds are diverted into the attacker's own shielded UTXO. This fits the Critical category ("direct theft of shielded or in-flight user funds"). The attack is repeatable against any Emporium-held position where settlement/claim is a separate step from order placement and is not restricted to a specific caller.

### Likelihood Explanation
Preconditions: Emporium must be the on-chain owner/maker of a position whose settlement requires an explicit claim/collect call not otherwise access-restricted beyond "authorized for Emporium" (true for Uniswap V3 `collect()` and many order-book `claim()` designs). Attacker only needs (a) knowledge of the victim's open position/order (observable on-chain), (b) enough of their own funds to generate a trivial valid Hinkal proof with `deltaAmountChanges == 0` for the target token, and (c) to submit before the victim's own claim tx — a standard front-running/racing scenario requiring no special privilege. Cost is a single gas-paying transaction; the win is stochastic on transaction ordering (mempool visibility / block builder), which is a realistic MEV scenario.

### Recommendation
Bind Emporium operations to an on-chain-recorded order/position owner rather than trusting arbitrary caller-supplied `externalActionMetadata`. Concretely: require `EmporiumStack.signerAddress` to always be non-zero and verified for any op that can settle/claim/collect from a pre-existing Emporium-held position, and/or maintain an on-chain mapping from position/order identifier to the depositor's committed stealth address / authorization, checked before `handleOut` distributes proceeds to `msg.sender`'s stealth address. At minimum, disallow the `signerAddress == address(0)` bypass for any `EmporiumOperation` whose target/selector is a known settlement/claim function on a registered external position.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as allowed recipient), and a mock Uniswap-V3-like `PositionManager`/order-book mock exposing `createOrder()` (Emporium as owner) and `collect()`/`claim()` gated by `isAuthorizedForToken(owner) == address(this)`ownership.
2. Victim (via a valid Hinkal proof) calls `transact` → `runAction` with ops `[createOrder()]`, depositing funds so Emporium becomes the position owner.
3. Attacker EOA directly interacts with the mock DEX/order-book (bypassing Hinkal entirely) to fill/cross the order so the position is "settled" but proceeds are only claimable, not yet transferred.
4. Attacker submits their own valid Hinkal proof (own UTXOs, `deltaAmountChanges[settledToken] == 0`) with `EmporiumStack{signerAddress: address(0), ops: [collect()]}` calling `runAction` before the victim's own claim transaction.
5. Assert: `handleOut`'s emitted `UTXO` for the settled token is credited to the attacker's `stealthAddressStructure`, and the victim's subsequent `collect()`-based `runAction` call now reverts/returns zero because the balance was already swept — proving `first caller of runAction != order-originating account` yet the caller captures the proceeds.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-79)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L80-83)
```text
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
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

**File:** contracts/HinkalHelper.sol (L208-228)
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
```
