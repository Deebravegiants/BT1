### Title
Emporium stateless op can drain any ERC20 that Emporium has approved to an attacker-controlled router, entirely outside the `erc20TokenAddresses`/`deltaAmountChanges` accounting - (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction`'s "stateless" branch (`op.invokeWallet==false || stack.signerAddress==address(0)`) lets any Hinkal user execute an arbitrary `op.endpoint.call(op.callData)` from Emporium's own address, with `msg.sender` inside that call being Emporium itself. [1](#0-0)  The only solvency guard against loss of Emporium's tokens is a before/after balance diff scoped strictly to `circomData.erc20TokenAddresses`, an array the attacker fully controls in their own proof/CircomData. [2](#0-1)  By omitting the target token from that array, the attacker can call a router that pulls tokens from Emporium via a previously-planted allowance, and no on-chain check (in `EmporiumUpgradeable.runAction` or `Hinkal.transact`) ever notices the token left the contract.

### Finding Description
The equality that should hold: for every ERC20 amount actually pulled from Emporium by an external call (`amountIn` via `transferFrom(Emporium, router, amountIn)`), there must be a corresponding entry in `circomData.erc20TokenAddresses` / `deltaAmountChanges` that the balance-diff checks validate. This equality is broken because both arrays are entirely attacker-supplied in their own proof and can simply omit the token being drained.

Code path:
1. `Hinkal.transact` → `_externalTransact` computes `deltaAmountChanges` only for indices present in `circomData.erc20TokenAddresses` and forwards to `EmporiumUpgradeable.runAction`. [3](#0-2) 
2. Inside `runAction`, for the stateless branch (`invokeWallet==false` or `signerAddress==address(0)`), the code directly does `op.endpoint.call{value: op.value}(op.callData)`, only blocking the `callHinkalWallet`/`doSendToRelay` selectors - any other call, including a swap-router call, is permitted. [1](#0-0) 
3. `verifyWallet` skips all signature/authorization checks entirely when `stack.signerAddress == address(0)`, only marking the message nonce used - so a completely unprivileged attacker can freely craft any `ops` sequence for the stateless path with no owner authorization needed. [4](#0-3) 
4. The only balance-safety check in `runAction` (`balancesBefore`/`balancesAfter`, `BalanceChangeShouldBePositive`) iterates over `circomData.erc20TokenAddresses` only. [5](#0-4)  If the attacker's proof declares an empty (or unrelated) `erc20TokenAddresses` array, this loop never executes for the stolen token.
5. `Hinkal.transact`'s outer balance-diff/slippage equality (`balanceDif == amountChanges + utxoAmount`) is likewise scoped only to `circomData.erc20TokenAddresses`. [6](#0-5) 
6. `HinkalHelper.performHinkalChecks`/`dimensionsCheck`/`checkOnchainCreation` validate array-length consistency and calldata-hash integrity, but never constrain what `op.endpoint`/`op.callData` in `externalActionMetadata` actually does at runtime, nor bind it to the declared token set. [7](#0-6) 

Given a pre-existing allowance `IERC20(token).allowance(Emporium, router) > 0` (settable by any attacker in an earlier stateless op that calls `token.approve(router, MAX)` from Emporium - an action that itself passes every check because `approve` doesn't move balance), the attacker can, in a later transaction, set `op.endpoint = router`, `op.callData = swapExactTokensForTokens(amountIn, ..., recipient=attacker, ...)`, and `circomData.erc20TokenAddresses = []` (or excluding `token`). The router call executes with `msg.sender == Emporium`, pulls `amountIn` of `token` out of Emporium via the allowance, and sends proceeds to the attacker. No balance/solvency check anywhere in `Hinkal.transact` or `EmporiumUpgradeable.runAction` observes this because the token was never declared.

### Impact Explanation
Any ERC20 balance held by the shared `EmporiumUpgradeable` contract (whether transient funds mid-multi-op-flight, dust from previous swaps/slippage, or balances left by other users' unfinished flows) can be drained by an unprivileged attacker to an address of their choosing. This is theft of protocol/user-controlled assets executed under an identity (Emporium's `msg.sender`) that the router implicitly trusts as token owner, without wallet-owner or prover authorization for that specific movement. Depending on what balance actually sits in Emporium at attack time, this qualifies as Critical (theft of in-flight/shielded user funds) or at minimum High (moving assets never authorized by any user). It is repeatable indefinitely as long as an exploitable allowance and non-zero Emporium balance of the target token exist.

### Likelihood Explanation
Preconditions: (a) an exploitable `allowance(Emporium, router) > 0` for some token — achievable unilaterally by the attacker via a prior stateless op with zero signature checks, and (b) a non-zero balance of that token sitting at Emporium at attack time. Both preconditions are attacker-influenceable/attacker-triggerable and require no privileged role, no victim key, and no cooperation from anyone else. The attack itself costs only gas for two Emporium transactions (plant approval, then drain) and is fully repeatable across tokens and routers.

### Recommendation
- In `EmporiumUpgradeable.runAction`, track and validate the *actual* token balance changes for every token touched by arbitrary `op.endpoint.call` (not just the attacker-declared `circomData.erc20TokenAddresses`), e.g. by requiring the full balance of Emporium never decreases for any token unless it is explicitly declared and accounted in `deltaAmountChanges`.
- Disallow (or heavily restrict) unauthenticated stateless calls with `signerAddress == address(0)` from setting `approve`/arbitrary allowances on behalf of the shared Emporium contract, or scope such approvals so they cannot be reused across unrelated transactions/attackers.
- Consider requiring stateless-branch `op.endpoint` to be an allow-listed router/target set by the owner, rather than any address chosen by the calling proof.

### Proof of Concept
Foundry fork test plan:
1. Deploy `EmporiumUpgradeable`, a mock ERC20 `TOKEN`, and a mock router `MockRouter` with `swapExactTokensForTokens` that does `TOKEN.transferFrom(msg.sender, address(this), amountIn)` and sends output to an arbitrary `to` param.
2. As attacker EOA, submit a Hinkal `transact` call to Emporium with `stack.signerAddress = address(0)`, one op: `endpoint = TOKEN`, `callData = approve(router, type(uint256).max)`, `erc20TokenAddresses = []`. Assert it succeeds and `TOKEN.allowance(Emporium, router) == max`.
3. Simulate a legitimate balance sitting at Emporium (e.g., have a victim's in-progress multi-op transaction leave `TOKEN` balance at Emporium, or directly fund Emporium via a prior legitimate flow) — assert `TOKEN.balanceOf(Emporium) == X > 0`.
4. As attacker, submit a second `transact` call: `stack.signerAddress = address(0)`, op: `endpoint = router`, `callData = swapExactTokensForTokens(X, ..., to=attacker, ...)`, `erc20TokenAddresses = []`, `deltaAmountChanges = []`.
5. Assert both sides of the broken equality: (a) `TOKEN.balanceOf(Emporium)` before vs after the second tx decreases by `X` (`amountIn` pulled by router), while (b) `circomData.erc20TokenAddresses` and `deltaAmountChanges` for that tx are both empty arrays containing no entry for `TOKEN` — proving the on-chain accounting never observed the loss.
6. Assert the second `transact` call succeeds without reverting `BalanceChangeShouldBePositive` or the `Hinkal.transact` slippage/balance-diff `require`, and that `TOKEN.balanceOf(attacker)` increased by the swap output — confirming successful, unaccounted theft.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-151)
```text
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

**File:** contracts/Hinkal.sol (L78-146)
```text
            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }

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
```

**File:** contracts/Hinkal.sol (L244-261)
```text
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
