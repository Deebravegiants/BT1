## Title
Dangling ERC20/Permit2-style allowance left by one Emporium `transact` CASE 2 operation can be drained by any other unprivileged user's `transact` call - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes attacker-controlled `EmporiumOperation.callData` via `op.endpoint.call{value: op.value}(op.callData)` with `msg.sender == Emporium`, and never revokes any allowance granted to a third-party spender during that call. [1](#0-0)  Because Emporium is a single shared, persistent contract across all users' `transact` calls (it is expected to carry a residual token balance between calls per the code's own comment), any leftover `approve` allowance from one user's op can be exploited by a completely unrelated, unprivileged attacker in a later `transact` call to steal Emporium's current balance of that token, and the theft is never captured by any accounting equation in either `EmporiumUpgradeable.runAction` or `Hinkal.transact`.

### Finding Description
Broken equality: for the attacker's own transaction, "tokens leaving Emporium during the action == -deltaAmountChanges it received for that token" (plus any tracked UTXO output). If the drained token is not included in the attacker's own `circomData.erc20TokenAddresses` array, no `balancesBefore`/`balancesAfter` measurement is ever taken for it, so the equality is never even evaluated — the tokens simply leave with zero accounting.

Code path:
1. A victim (or any earlier user) submits a CASE 2 stateless op via `transact`. `verifyWallet` performs no signature check at all when `stack.signerAddress == address(0)`, so CASE 2 stateless ops require no privileged signer — only the caller's own valid ZK proof for their own UTXOs. [2](#0-1) 
2. In `runAction`, CASE 2 executes `op.endpoint.call{value: op.value}(op.callData)` with only a check that the selector isn't `callHinkalWallet`/`doSendToRelay` — any other call, including `IERC20.approve` or a Permit2 `approve(token, spender, amount, expiration)`, is allowed, and since `msg.sender` of that call is Emporium, the resulting allowance owner is Emporium. [1](#0-0) 
3. Nothing in the ops loop or afterward revokes this allowance. The only allowance-clearing helpers in the codebase, `unsafeApproveERC20Token`/`approveERC20Token`/`approveUnlimited`, are internal functions never invoked from this CASE 2 path. [3](#0-2) [4](#0-3) 
4. The balance check that follows only covers tokens present in `circomData.erc20TokenAddresses` for that specific call, and the accompanying comment explicitly acknowledges Emporium can already be holding a balance before the call ("the only case when balanceChange can be < 0, when there were some funds on emporium before the call"), confirming Emporium's balance is expected to persist across unrelated transactions. [5](#0-4) 
5. An unprivileged attacker later calls `transact` with their own CASE 2 op targeting the same `endpoint` (the Permit2-style/spender contract) with `callData = transferFrom(Emporium, attacker, amount)` (or Permit2's equivalent), draining Emporium's balance of the token directly to the attacker. If the attacker simply omits that token from their own `erc20TokenAddresses` array, neither `EmporiumUpgradeable.runAction`'s balance loop nor `Hinkal.transact`'s balance-diff/slippage loop (`contracts/Hinkal.sol:97-147`) ever inspects that token, so the stolen amount is never checked against any `deltaAmountChanges`/`amountChanges`/`utxoAmount` value. [6](#0-5) 

Existing guards do not prevent this: `performHinkalChecks`, `verifyProof`, `rootHashExists`, `insertNullifiers`, and the balance-diff/slippage requires in `Hinkal.transact` all operate strictly on the caller's own declared `circomData.erc20TokenAddresses`/`amountChanges`/`deltaAmountChanges`, none of which reference the leftover allowance or the drained token if it's excluded from the array. [7](#0-6) 

### Impact Explanation
Direct theft of another user's/protocol's shielded-in-flight token balance held on the shared Emporium contract, by an unprivileged attacker, with zero corresponding entry in the attacker's own proof-verified `deltaAmountChanges`/UTXO set — this is unauthorized asset movement never authorized by any prover or wallet owner, matching the Critical category (direct theft of shielded/in-flight user funds). The attack is repeatable any time a dangling allowance plus a nonzero Emporium balance of that token coexist, and is not limited to a single victim — it can drain any token Emporium happens to hold at the time.

### Likelihood Explanation
Preconditions: (1) some prior CASE 2 op (from any user, benign integration such as a DEX/Permit2 swap that leaves excess allowance, e.g., due to slippage-tolerant approve-then-swap flow) leaves `allowance(Emporium, spender) > 0` on some endpoint/token; (2) Emporium currently holds a nonzero balance of that token (explicitly anticipated by the contract's own comments). Both are plausible in normal operation given the unrestricted, unallowlisted `op.endpoint`/`op.callData` design for CASE 2. Attacker cost is a single `transact` call with a valid proof for their own (possibly trivial/zero) UTXOs — no special privileges, no victim cooperation, and fully repeatable each time the precondition recurs.

### Recommendation
- After each CASE 2 (and CASE 1) op in `EmporiumUpgradeable.runAction`, explicitly reset any allowance the op may have granted to third parties (e.g., require ops to use an allowance-scoped pattern, or force-zero `IERC20(token).approve(spender, 0)` for every `(token, spender)` pair touched by an op immediately after use).
- Alternatively/additionally, restrict `op.endpoint` to an allowlisted registry of vetted integration contracts, and require that any approval granted during an op is fully consumed or explicitly revoked before the transaction completes (e.g., verify `allowance == 0` post-call for tokens that had an approval set during the op).
- Track and check balances for every token that had any allowance modified during the ops loop, not only the tokens declared in `circomData.erc20TokenAddresses`, so unaccounted-for balance loss cannot bypass the loop in `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:132-151`.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, a mock ERC20 `token`, and a mock Permit2-style `endpoint` contract with `approve(token, spender, amount)` (owner-scoped storage keyed by `msg.sender`) and `transferFrom(from, to, amount, token)` that checks its internal allowance mapping.
2. Fund Emporium with `token` (simulate residual balance from prior in-flight deposits).
3. "Victim" transaction: call `transact` with a CASE 2 `EmporiumOperation` (`signerAddress == address(0)`, `invokeWallet == false`) whose `callData` is `endpoint.approve(token, mockSpender, amount)`; assert `endpoint.allowance(address(Emporium), token, mockSpender) == amount` after the call, and that this token is not in the victim's own `erc20TokenAddresses` (or that balance loop passes trivially since balance is unchanged).
4. "Attacker" transaction, in a separate `transact` call: submit a CASE 2 op with `callData = endpoint.transferFrom(address(Emporium), attacker, amount, token)`, and set `circomData.erc20TokenAddresses` for this call to exclude `token` (e.g., only ETH or an unrelated placeholder token with `amountChanges == 0`).
5. Assert: `token.balanceOf(attacker)` increases by `amount`; `token.balanceOf(Emporium)` decreases by `amount`; the attacker's proof-verified `deltaAmountChanges`/`amountChanges` for `token` is `0` (or the token doesn't appear at all in the attacker's declared arrays); the `transact` call succeeds without reverting on any balance/slippage `require` in `contracts/Hinkal.sol:111-146` or `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:132-151`.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-118)
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

            if (!success) {
                revert CallFailed(err);
            }
        }
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

**File:** contracts/Transferer.sol (L48-55)
```text
    function unsafeApproveERC20Token(
        address _erc20TokenAddress,
        address _to,
        uint256 _value
    ) internal {
        IERC20(_erc20TokenAddress).approve(_to, 0);
        IERC20(_erc20TokenAddress).approve(_to, _value);
    }
```

**File:** contracts/TransfererBase.sol (L23-43)
```text
    function approveERC20Token(
        address _erc20TokenAddress,
        address _to,
        uint256 _value
    ) internal {
        IERC20(_erc20TokenAddress).safeApprove(_to, 0);
        IERC20(_erc20TokenAddress).safeApprove(_to, _value);
    }

    function approveUnlimited(
        address _erc20TokenAddress,
        address _to
    ) internal {
        if (
            IERC20(_erc20TokenAddress).allowance(address(this), _to) <
            type(uint256).max / 2
        ) {
            IERC20(_erc20TokenAddress).safeApprove(_to, 0);
            IERC20(_erc20TokenAddress).safeApprove(_to, type(uint256).max);
        }
    }
```

**File:** contracts/Hinkal.sol (L97-147)
```text
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
