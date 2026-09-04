### Title
Arbitrary unauthenticated external call in Emporium's "Stateless Interaction" path lets any caller plant a hidden `approve()` on the shared Emporium contract, later draining any token balance it holds - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes attacker-controlled `endpoint`/`callData` pairs directly from the shared Emporium contract whenever `EmporiumStack.signerAddress == address(0)`, with **zero signature/authorization requirement** for that branch. Because the post-call balance reconciliation only checks the tokens explicitly listed in `circomData.erc20TokenAddresses` for that single transaction, and because operations like `approve()` don't move any balance, an attacker can smuggle an unlimited `ERC20.approve(attacker, type(uint256).max)` call from the Emporium contract for any token, entirely undetected by the equality check, and later drain whatever balance of that token the shared contract ever holds.

### Finding Description
`runAction` decodes an `EmporiumStack` from `circomData.externalActionData.externalActionMetadata` and, for each `EmporiumOperation`, either calls through the user's per-signer `HinkalWallet` (CASE 1) or calls `op.endpoint` directly from the Emporium contract itself when `invokeWallet` is false or `signerAddress == address(0)` (CASE 2): [1](#0-0) 

`verifyWallet` is the only gate on these ops, but it explicitly skips *all* signature verification when `signerAddress == address(0)`: [2](#0-1) 

The only remaining safety net is the balance-delta reconciliation performed after all ops run: [3](#0-2) 

This loop only iterates over `circomData.erc20TokenAddresses` — the token list supplied for *that* transaction — and only rejects a **negative** net balance change. An `approve()` call does not change `balanceOf`, so it is invisible to this equation regardless of whether the target token is even included in `erc20TokenAddresses`. Since the "min" Emporium path explicitly allows `erc20TokenAddresses.length == 0` (`CircomDataBuilder.formInputEmporiumMin`), an attacker can submit a transaction with an empty token list and a single op that sets `IERC20(anyToken).approve(attacker, type(uint256).max)` on behalf of the Emporium contract — no balance check runs at all, and no signature is required because `signerAddress` is zero.

Because `EmporiumUpgradeable` is a shared, non-per-user contract (unlike the per-signer `HinkalWallet`), any residual balance it later holds for *any* token — dust from rounding, a mid-flight deposit from another concurrent transaction, or protocol/relay fee tokens momentarily routed through it — becomes stealable via a plain `transferFrom(emporium, attacker, amount)` call made directly by the attacker outside of Hinkal, using the previously planted approval. This is unauthorised asset movement that neither the zk proof, the EIP-712 signature (skipped for `signerAddress == 0`), nor the in-transaction balance equation ever accounts for.

This mirrors the reported Kame bug class: an aggregator-style `swap`/`runAction` call accepts an attacker-supplied `executor`/`executeParams` (here `op.endpoint`/`op.callData`) and executes it with no meaningful restriction on what the call can do.

### Impact Explanation
This meets the High/Critical bar: it is an "executing calls or moving assets ... never authorised" by any signer, and results in theft of protocol/pooled funds (dust, relay fees, or any balance transiently held by the shared Emporium contract) via a self-planted, persistent ERC20 approval that completely bypasses both the EIP-712 signer check and the in-tx balance equation.

### Likelihood Explanation
Any unprivileged EOA can trigger this by generating their own valid zk proof for a normal `transact()` call (no relayer/admin/owner keys needed), setting the Emporium `externalActionId`, `erc20TokenAddresses = []` (permitted by `formInputEmporiumMin`), and `EmporiumStack.signerAddress = address(0)` with one op calling `approve()` on an arbitrary token from the Emporium contract. The subsequent drain requires the target token to actually accrue a balance on the shared contract, which depends on operational timing/dust but is a realistic and recurring condition for a shared, stateful pool contract.

### Recommendation
- Require `verifyWallet` to authenticate every op (including `signerAddress == address(0)`) against the depositor themself (e.g., bind to `circomData.originalSender`/prover identity), rather than skipping authorization entirely.
- Restrict "Stateless Interaction" `op.endpoint.call` targets to a strict allow-list of known router/endpoint addresses and disallow arbitrary selectors like `approve`, or force `approve`s to be reset to zero at the end of `runAction`.
- Extend the post-call reconciliation to also check allowances granted by the Emporium contract during the call (or forbid `approve` selector entirely in ops), not just token balances of the listed `erc20TokenAddresses`.

### Proof of Concept
1. Attacker crafts `circomData` for `Hinkal.transact()` targeting the Emporium `externalActionId`, with `erc20TokenAddresses = []` (valid per `formInputEmporiumMin`, since `circomData.erc20TokenAddresses.length == 0`) — [4](#0-3) .
2. `externalActionData.externalActionMetadata` encodes an `EmporiumStack` with `signerAddress = address(0)` and one `EmporiumOperation{ endpoint: <victimToken>, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max) }`.
3. Attacker generates a normal, self-consistent zk proof (their own transaction, no special privilege) so `calldataHash` matches and the proof verifies.
4. `Hinkal.transact()` → `_externalTransact` → `EmporiumUpgradeable.runAction` runs; `verifyWallet` returns immediately (`signerAddress == 0`) with no signature check — [5](#0-4) ; the empty `erc20TokenAddresses` loop performs no balance check — [6](#0-5) ; `op.endpoint.call(op.callData)` executes the `approve()` from the Emporium contract — [7](#0-6) .
5. Whenever the Emporium contract subsequently holds any balance of `victimToken` (dust, fee remnants, or a concurrent deposit), attacker calls `victimToken.transferFrom(emporium, attacker, amount)` directly, draining funds never authorised by any Hinkal proof or signer for that balance.

### Citations

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

**File:** contracts/CircomDataBuilder.sol (L139-161)
```text
        if (
            circomData.externalActionData.externalActionId ==
            HINKAL_EMPORIUM_ACTION_ID &&
            circomData.erc20TokenAddresses.length == 0
        ) {
            return formInputEmporiumMin(circomData);
        } else {
            return formInputNormal(chainId, verifyingContract, circomData);
        }
    }

    function formInputEmporiumMin(
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);

        uint16 index = 0;

        input[index++] = circomData.emporiumMessage;

        input[index++] = circomData.timeStamp;
        input[index++] = circomData.calldataHash;
    }
```
