## Analysis

This is an unprivileged-EOA analog to the reported bug class: a user-controlled parameter list determines what gets balance-checked, while an *arbitrary* value-moving operation is permitted outside that checked set — exactly the "value moved by Hinkal or an external action but not counted in the balance equation" analog category.

### Root cause

`EmporiumUpgradeable.runAction()` lets any transaction routed through the Emporium (reachable by any unprivileged user calling `Hinkal.transact()` with `externalActionId` set to Emporium — `onlyAllowedRecipient` only checks `msg.sender == Hinkal`, not any special privilege) execute arbitrary calls from the Emporium contract itself: [1](#0-0) 

In the "Stateless Interaction" branch, `op.endpoint.call{value: op.value}(op.callData)` executes with `msg.sender == Emporium`, so if `op.endpoint` is any ERC20 token contract and `op.callData` is `transfer(attacker, amount)`, tokens owned by the Emporium contract are sent out — no approval or wallet authorization needed, since it's `transfer`, not `transferFrom`.

The only safety net is the post-call balance-invariant check: [2](#0-1) 

That loop iterates **only over `circomData.erc20TokenAddresses`**, an array the attacker supplies as part of their own proof/calldata. Any token not included in that list is never balance-checked, so a drain of that token via the stateless call goes completely undetected by Emporium.

Critically, `Hinkal.sol`'s own balance-invariant check (`transact()`) also only iterates `circomData.erc20TokenAddresses` and only checks **Hinkal's own balance**, not the Emporium's: [3](#0-2) 

So a token balance sitting at the Emporium address (residual dust from prior swaps/ops that weren't fully swept by `handleOut`, or any tokens/ETH otherwise present at that address) can be drained by any user by simply omitting that token from their own `erc20TokenAddresses` list and issuing a stateless op that calls `transfer` on it. Neither Emporium's own invariant nor Hinkal's global invariant will catch or block this, because the checked-token set is entirely attacker-chosen and disjoint from the token being stolen.

### Title
Emporium `runAction` stateless-call path allows draining any token balance held by the Emporium contract that the attacker excludes from their own `erc20TokenAddresses` list - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction()`'s "Case 2: Stateless Interaction" lets an attacker execute an arbitrary `endpoint.call(callData)` with `msg.sender == Emporium`. The subsequent balance-invariant guard (`BalanceChangeShouldBePositive`) only checks tokens listed in the attacker-supplied `circomData.erc20TokenAddresses`, and `Hinkal.sol`'s own invariant likewise only checks its own balance for the same attacker-chosen list. Any token an attacker omits from that list is never balance-checked at either layer, so a `transfer()` call moving that token out of Emporium to the attacker is undetected and unauthorized by any prover/signer.

### Finding Description
`runAction` computes `balancesBefore`/`balancesAfter` and enforces `balanceChange >= 0` only for `circomData.erc20TokenAddresses` [4](#0-3) . This array is chosen by the caller and is not tied by the circuit/signature to the set of `op.endpoint`/`op.callData` targets actually invoked in the stateless branch [1](#0-0) . An attacker can therefore craft `circomData.erc20TokenAddresses` to exclude the token they intend to steal, while their `ops` array contains a call to that token's `transfer(attacker, balance)` — moving value out of Emporium with no equality check ever validating it.

### Impact Explanation
Any ERC20/ETH balance resident at the Emporium address (e.g., residual dust left by imperfect sweeps of prior swap/emporium operations, tokens sent directly to that address, or protocol/relay fee tokens awaiting `sendToRelay`) can be permanently stolen by any unprivileged user. This is unauthorized asset movement never sanctioned by any prover or signer, matching High/Critical impact: theft of protocol/relay fees or in-flight funds sitting at a shared contract address.

### Likelihood Explanation
Reachable by any ordinary user through the standard `Hinkal.transact()` flow with `externalActionId` set to Emporium and a valid proof for their own (possibly trivial/zero) UTXOs — no admin, relay, or other user's key is required, only crafting `circomData.erc20TokenAddresses` and `ops` appropriately.

### Recommendation
Enumerate and account for balance changes of every token actually touched by `op.endpoint`/`op.callData` (or restrict stateless-call targets to a controlled allowlist), rather than only the attacker-supplied `circomData.erc20TokenAddresses`, and ensure `Hinkal.sol`'s invariant also reflects the external action contract's balance, not just its own.

### Proof of Concept
1. Some token `T` balance exists at the Emporium contract address (dust/leftover from a prior transaction, or any inbound transfer).
2. Attacker calls `Hinkal.transact()` with `externalActionId` = Emporium, `circomData.erc20TokenAddresses` = `[]` or any list excluding `T`, and a valid proof for a trivial/no-op shielded transaction of their own.
3. `circomData.externalActionData.externalActionMetadata` encodes an `EmporiumStack` with one stateless `EmporiumOperation{ endpoint: T, invokeWallet: false, callData: abi.encodeWithSelector(IERC20.transfer.selector, attacker, T.balanceOf(Emporium)) }`.
4. `EmporiumUpgradeable.runAction()` executes the call (`msg.sender == Emporium`), transferring all of `T` to the attacker; the balance-invariant loop never inspects `T` since it isn't in `erc20TokenAddresses`, and `Hinkal.sol`'s own invariant also never inspects `T` or Emporium's balance.

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

**File:** contracts/Hinkal.sol (L88-146)
```text
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
