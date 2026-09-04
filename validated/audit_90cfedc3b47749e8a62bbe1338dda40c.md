### Title
Attacker-controlled `EmporiumStack.ops` in stateless (`signerAddress == address(0)`) mode can drain any residual/stranded token balance from `EmporiumUpgradeable` by simply omitting that token from `erc20TokenAddresses` - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` only checks the invariant "tokens leaving the action == `-deltaAmountChanges`" for tokens listed in `circomData.erc20TokenAddresses`, an array fully controlled by the calling user. When `stack.signerAddress == address(0)`, `runAction`'s "Stateless Interaction" branch executes `op.endpoint.call{value: op.value}(op.callData)` directly from the `EmporiumUpgradeable` contract with no signature and no constraint linking `op.endpoint`/`op.callData` to any declared token. An attacker can therefore craft an op that transfers any token currently parked in `EmporiumUpgradeable` (e.g., a router-refund residual left by a prior transaction) straight to their own address, while excluding that token from `erc20TokenAddresses` so the balance-diff check in `runAction` (and the mirrored one in `Hinkal.transact`) never examines it.

### Finding Description
The equality that should hold: for every token that leaves the action contract during a transaction, `balanceChange[token] == -deltaAmountChanges[token]` (net of amounts routed to a UTXO out).

This is enforced only inside the loop: [1](#0-0) 
which iterates exclusively over `circomData.erc20TokenAddresses`. The same scoping happens in `Hinkal.transact`'s balance-diff loop: [2](#0-1) 
Both loops trust the caller-supplied `circomData.erc20TokenAddresses` array to enumerate every token whose balance is affected. Nothing in `performHinkalChecks`/`dimensionsCheck`/`verifyProof` ties the opaque `op.endpoint`/`op.callData` bytes (decoded from attacker-supplied `externalActionMetadata`) to the declared token list, because the circuit cannot know in advance which tokens an arbitrary external call will touch.

The "Stateless Interaction" branch performs the raw call with zero authorization when there is no wallet signer: [3](#0-2) 
and `verifyWallet` skips all signature checks in this mode, only marking `emporiumMessage` used: [4](#0-3) 

Exploit flow:
1. `EmporiumUpgradeable` accumulates a stranded/residual balance of `tokenX` (e.g., a router refund from a prior swap that was not fully swept, or simply dust from any earlier action).
2. An unprivileged attacker submits their own valid Hinkal proof/deposit (any small unrelated UTXO), setting `circomData.externalActionData.externalActionMetadata` to an `EmporiumStack` with `signerAddress == address(0)` and one op: `endpoint = tokenX`, `callData = abi.encodeCall(IERC20.transfer, (attacker, residualAmount))`.
3. The attacker deliberately omits `tokenX` from `circomData.erc20TokenAddresses` (they only list the token(s) actually needed for their own legitimate deposit/output).
4. `runAction` executes the op, transferring `residualAmount` of `tokenX` directly from `EmporiumUpgradeable` to the attacker's EOA. Because `tokenX` is absent from `erc20TokenAddresses`, neither `EmporiumUpgradeable`'s balance loop nor `Hinkal.transact`'s balance loop ever inspects it — no `BalanceChangeShouldBePositive` revert, no slippage/balance-diff requirement applies.
5. The attacker's own declared tokens still balance correctly, so their transaction passes all remaining checks (`verifyProof`, `rootHashExists`, balance-diff on declared tokens, nullifier insertion) unaffected.

This breaks the stated invariant for any token not in the attacker-chosen list, and is not limited to strictly "residual" amounts — any balance the contract happens to hold (including funds another user's in-flight action deposited into `EmporiumUpgradeable` just before, via `_externalTransact`'s pre-transfer at contracts/Hinkal.sol lines 247-255) is momentarily exposed to this drain if an attacker's transaction executing in the same or a later block interacts with the shared contract before that balance is fully consumed by its own legitimate ops.

### Impact Explanation
Direct theft of tokens held by `EmporiumUpgradeable` that do not belong to the attacker — this includes protocol/relay-parked residuals and, depending on transaction ordering within a block, funds momentarily resident in the shared action contract for another user's in-flight swap. This matches the Critical category "direct theft of shielded or in-flight user funds." The attack is repeatable every time the contract holds a non-zero balance of any token, at negligible cost (one valid Hinkal transaction with the attacker's own funds/proof).

### Likelihood Explanation
Preconditions: `EmporiumUpgradeable` must hold a non-zero balance of some ERC20/ETH not needed for the attacker's own claimed tokens — a routine occurrence given `_externalTransact` pre-funds the action before `runAction` runs, and any router/DEX interaction that doesn't perfectly consume its input can leave dust. The attacker needs no privileged role: they only need to produce a valid proof for their own UTXO/deposit and freely craft `externalActionMetadata` (explicitly listed as attacker-controlled in the target scope) and `erc20TokenAddresses`. No wallet signature is required in the `signerAddress == address(0)` path. This is fully feasible and repeatable each block that presents a non-zero opportunistic balance.

### Recommendation
- Do not allow arbitrary `op.endpoint.call` in the stateless path unless `op.endpoint` is restricted to a governance-controlled allowlist (e.g., known DEX routers) that cannot arbitrarily move ERC20 balances to attacker-chosen addresses.
- Enumerate/verify, after each op, that the resulting balance changes for ALL tokens actually held/touched by `EmporiumUpgradeable` (not just attacker-declared `erc20TokenAddresses`) are accounted for — e.g., snapshot the full set of tokens with non-zero balance before/after and require any decrease to correspond to a declared `deltaAmountChanges` entry.
- Alternatively, sweep/settle any residual balance to a protocol-controlled address immediately after every action (rather than leaving it parked in the shared contract) so no exploitable window exists between transactions.
- Require `circomData.erc20TokenAddresses` to be validated against the actual token balance deltas of the contract by iterating over a fixed/administered token registry rather than a caller-supplied list.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (proxy), a mock ERC20 `tokenX`, register `EmporiumUpgradeable` as allowed external action and allowed recipient.
2. Seed the residual: directly `tokenX.mint(address(emporium), 1000e18)` (simulating a stranded router refund from a prior action) without any corresponding UTXO/ownership.
3. As `attacker` (unprivileged EOA), construct a valid Hinkal `transact` call:
   - `circomData.erc20TokenAddresses` = `[tokenY]` (some unrelated token attacker legitimately deposits/withdraws), deliberately excluding `tokenX`.
   - `circomData.externalActionData.externalActionMetadata` = ABI-encoded `EmporiumStack{ signerAddress: address(0), ops: [ {endpoint: tokenX, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 1000e18))} ] }`.
   - Generate a valid proof/circuit inputs for the attacker's own `tokenY` UTXO in/out amounts (using the repo's existing proof-generation test harness).
4. Call `Hinkal.transact(...)`.
5. Assertions:
   - Before: `tokenX.balanceOf(emporium) == 1000e18`, `tokenX.balanceOf(attacker) == 0`.
   - After: `tokenX.balanceOf(emporium) == 0`, `tokenX.balanceOf(attacker) == 1000e18`.
   - Transaction succeeds without reverting on `BalanceChangeShouldBePositive` or "slippage param is violated", proving the invariant `tokens leaving the action in this tx == -deltaAmountChanges Hinkal sent it this tx` is violated for `tokenX` (whose `deltaAmountChanges` entry doesn't even exist since it wasn't declared).

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
