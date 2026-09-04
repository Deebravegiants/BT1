## Finding [1](#0-0) 

### Title
Arbitrary `ops[].endpoint.call` in `EmporiumUpgradeable.runAction` can drain any ERC-20 token not listed in `circomData.erc20TokenAddresses`, bypassing the balance-equality check — (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` executes an attacker/prover-supplied list of `EmporiumOperation` calls (`op.endpoint.call{value: op.value}(op.callData)`) with **no restriction on the destination address or the token it touches**. The only safety check afterward is a balance-delta loop that iterates strictly over `circomData.erc20TokenAddresses` — an array fully chosen by the same unprivileged prover who submits the transaction. Any token the prover simply omits from that array is invisible to the `BalanceChangeShouldBePositive` check, so an operation that drains that token's balance from the Emporium contract is never caught, mirroring the `MulticallWithoutCheck` pattern where an unrestricted external call let anyone move a held token balance out of the target contract.

### Finding Description
In the stateless branch (`stack.signerAddress == address(0)`), `verifyWallet` only marks `circomData.emporiumMessage` as used and returns — no signature or extra authorization is required beyond the prover's own ZK proof of spending their own (arbitrarily small) UTXO: [2](#0-1) 

The loop that executes ops then makes an **unconstrained** external call for every stateless op: [3](#0-2) 

The only bookkeeping is: [4](#0-3) 

and `handleOut`/the revert guard only look at `balancesBefore`/`balancesAfter` for `circomData.erc20TokenAddresses` — an array the same unprivileged prover fully controls when constructing their own `CircomData` (it is only bound into `calldataHash`/`signedMessageHash`, so a self-consistent proof over *any* chosen token set is trivially valid for the prover themselves): [5](#0-4) 

Because the Emporium contract is designed to legitimately retain leftover balances between calls (per the code comment "the only case when balanceChange can be < 0, when there were some funds on emporium before the call"), any ERC-20 token that ends up sitting on the Emporium contract (dust from partial ops, relay-fee tokens, rounding remainders from prior legitimate transactions) is a target: a prover simply excludes that token from `erc20TokenAddresses` and adds an op `token.transfer(attacker, emporiumBalance)`. Since that token never appears in `balancesBefore`/`balancesAfter`, the drain produces no negative delta and never trips `revert BalanceChangeShouldBePositive()`. The stolen tokens leave the contract with no corresponding UTXO nullifier/commitment accounting for them — this breaks the balance equation the same way the `MulticallWithoutCheck` exploit broke Target's balance (an unrestricted external call moves out tokens that were never authorized to be moved by that caller).

### Impact Explanation
This is a direct theft of protocol/relay-fee or other users' funds accumulated on the `EmporiumUpgradeable` contract, executed by any unprivileged EOA using only their own (arbitrarily small) shielded UTXO to generate a valid proof — no signer approval, admin key, or relayer collusion required. Per the rules this is Critical/High: theft of protocol or relay fees, and unauthorized asset movement never counted by the balance equation.

### Likelihood Explanation
The precondition is that the Emporium contract holds a nonzero balance of some ERC-20 token outside the current transaction's declared `erc20TokenAddresses` set (e.g., relay-fee remainders, rounding dust from prior swaps/deposits, or ETH from `receive()`). Given the contract's own code comments acknowledge pre-existing balances are expected, and its lifetime (not a one-shot ephemeral contract) makes accumulation likely over many transactions, exploitation requires no special privilege — just crafting `stack.ops` with an extra call to the target token's `transfer`, `approve`+`transferFrom`, or similar and choosing `erc20TokenAddresses` to omit it.

### Recommendation
Restrict the balance check to include *every* ERC-20 token touched by any `op.endpoint` (or, simpler, whitelist admissible endpoints/selectors and require every token balance change on the Emporium contract — not just those in `erc20TokenAddresses` — to be captured and either reverted or attributed to a UTXO). Alternatively, enforce that the Emporium contract never carries a standing balance across transactions (sweep to zero at the end of `runAction`, or restrict ops to only interact with tokens explicitly present in `circomData.erc20TokenAddresses`).

### Proof of Concept
1. Wait until (or arrange for, e.g. via a normal prior legitimate deposit that leaves rounding dust) the `EmporiumUpgradeable` contract holds a balance of `TOKEN_X` from unrelated prior activity.
2. As any unprivileged EOA, generate a valid Hinkal proof spending a trivial owned UTXO of a different token, `TOKEN_Y`, with `circomData.erc20TokenAddresses = [TOKEN_Y]` (deliberately excluding `TOKEN_X`).
3. Set `circomData.externalActionData.externalActionMetadata` to an `EmporiumStack` with `signerAddress = address(0)` and `stack.ops = [{ endpoint: TOKEN_X, callData: abi.encodeWithSignature("transfer(address,uint256)", attacker, emporiumBalanceOfTokenX), value: 0 }]`.
4. Call `transact` on `Hinkal.sol`, which routes to `EmporiumUpgradeable.runAction`. The op executes and transfers `TOKEN_X` out to the attacker; because `TOKEN_X` is not in `erc20TokenAddresses`, `balancesBefore`/`balancesAfter` never observe the change and the `BalanceChangeShouldBePositive` guard never fires.
5. Attacker keeps the drained `TOKEN_X` with no debit against any shielded balance.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-118)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-150)
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

**File:** contracts/CircomDataBuilder.sol (L20-35)
```text
    function getHashedCalldata1(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.publicSignalCount,
                        circomData.relay,
                        circomData.emporiumMessage,
                        circomData.externalActionData,
                        circomData.slippageValues
                    )
                )
            );
    }
```
