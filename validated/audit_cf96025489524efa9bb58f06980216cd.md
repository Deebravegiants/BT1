### Title
Emporium's per-call balance safety net only covers the caller-chosen token list, letting an attacker drain any resident balance/allowance via an unlisted-token CASE‑2 call - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` (and the outer `Hinkal.transact` balance check) only compares before/after balances for the tokens the *current caller* declares in `circomData.erc20TokenAddresses`. Because `EmporiumOperation.endpoint`/`callData` in a stateless (CASE 2) op can target any contract with any calldata (only the two `IHinkalWallet` selectors are blocked), an attacker can craft ops that move a token that is *not* in their own declared token list, so neither the Emporium-level nor the Hinkal-level balance/slippage invariants ever observe the change.

### Finding Description
The claimed equality: `set(tokens whose Emporium balance is protected by the runAction/transact balance check) == set(tokens whose balance can actually change during the ops loop)`.

This equality does not hold:
- The safety checks are:
  - Emporium: `balancesBefore`/`balancesAfter` computed only over `circomData.erc20TokenAddresses` [1](#0-0) .
  - Hinkal: `oldBalances`/`newBalances` and the `balanceDif == amountChanges[i] + utxoAmount` invariant, again scoped to `circomData.erc20TokenAddresses` [2](#0-1) .
- `circomData.erc20TokenAddresses` is fully attacker-chosen; the only circuit-level constraint on it is that entries be pairwise distinct (`distinctErc20AddressChecks`) and match `dimensions.tokenNumber` in length [3](#0-2) [4](#0-3) . Per-token spend is only enforced when `inAmounts[i][j] != 0` (`calcEqual[i][j].enabled <== inAmounts[i][j]`), so an attacker can include a token in the array with all-zero amounts and no real UTXO ownership, or simply omit any token entirely [5](#0-4) .
- Inside the ops loop, CASE 2 only blocks `callHinkalWallet`/`doSendToRelay` selectors; any other `endpoint.call(callData)` is permitted, including `token.approve(router, type(uint256).max)` or `router.swap(...)` [6](#0-5) .
- Because Emporium is a single shared, stateful contract (its ERC20 allowances and any un-swept token balances persist across unrelated transactions/users — nothing sweeps or resets allowances/dust between calls), any token X for which Emporium currently holds a balance and/or has an outstanding allowance to a router (granted by a prior approve op from any past `runAction`, or even self-granted by the attacker within the same call since the approve call itself is unguarded) can be moved by a CASE‑2 op that calls that router directly with `recipient` set to the attacker.
- If the attacker's own `circomData.erc20TokenAddresses` array omits token X, the Emporium `getBalancesForArray`/`balanceChange` loop never inspects X, so `BalanceChangeShouldBePositive` never fires, and the outer Hinkal `balanceDif` check also never inspects X. The attacker's ZK proof/dimensions only need to be consistent for the tokens they *do* list (e.g., a zero-amount or self-owned token Y), which is fully achievable with the attacker's own valid UTXOs.
- Result: value that was never part of the attacker's proof (protocol/relay-adjacent dust, leftover intermediate-hop tokens from other users' swaps, or fee tokens sitting in Emporium) can be pulled out of Emporium and redirected to the attacker through a router call whose only real precondition is a live allowance — a call the wallet owner/prover never authorised and that is invisible to every accounting check in this file and in `Hinkal.transact`.

### Impact Explanation
An attacker can extract ERC20 balances resident in the shared `EmporiumUpgradeable` contract (protocol/relay fee remnants or unswept intermediate-hop dust from other users' operations) without any of that value being reflected in their own proof's `amountChanges`/UTXO outputs, and without ever needing the token in their declared `erc20TokenAddresses` array. This is an "executing calls / moving assets never authorised by a wallet owner or prover" and "theft of protocol/relay fees" scenario — matching the High severity bar. The action is repeatable for every token that accumulates a nonzero resident balance and has (or can be given, via a self-crafted approve op) an active allowance to an attacker-reachable router.

### Likelihood Explanation
Preconditions: (1) Emporium must actually hold a nonzero balance of the target token — this depends on other operational flows leaving dust/fees behind (a plausible and common occurrence with multi-hop router swaps and partial-fill scenarios that don't list every intermediate token); (2) a persisted allowance to a controllable router, which the attacker can *also self-create in the same transaction* since CASE‑2 approve calls are unrestricted. Attacker cost is a single valid Hinkal `transact` call with a legitimate proof over their own (possibly zero-value) UTXOs plus a crafted `EmporiumStack`; no privileged role or victim cooperation is required. Feasibility is high and the attack is repeatable across tokens/balances as they accumulate.

### Recommendation
- Track and enforce balance invariants over the *full set of tokens actually touched* by the ops (e.g., by requiring `circomData.erc20TokenAddresses` to include every token targeted by any `op.endpoint`/token referenced in `op.callData`, or by snapshotting/comparing balances for a fixed allow-list of tokens rather than an attacker-chosen list).
- Restrict CASE‑2 stateless calls to a whitelist of endpoints (e.g., only pre-approved routers/tokens set by governance) instead of arbitrary attacker-supplied `endpoint`/`callData`.
- Do not allow standing/infinite approvals from Emporium to persist across transactions — revoke (`approve(router, 0)`) at the end of each `runAction`, or require exact-amount approvals scoped to the current call.
- Sweep any un-tracked residual balances after each transaction rather than leaving them stranded in the shared Emporium contract.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, a mock ERC20 `TokenX`, `TokenY`, and a mock router `Router` with a `swap(tokenIn, tokenOut, amountIn, recipient)` function that does `TokenX.transferFrom(msg.sender, address(this), amountIn)` then `TokenY.transfer(recipient, amountOut)`.
2. Seed Emporium with a resident `TokenX` balance (simulating dust/fees from a prior unrelated op) by directly minting/transferring `TokenX` to the Emporium address, bypassing `runAction`'s own accounting (representing funds that never got swept out because a prior caller's `erc20TokenAddresses` didn't include `TokenX`).
3. Craft an attacker `CircomData`/`EmporiumStack` with:
   - `circomData.erc20TokenAddresses = [TokenY]` only (TokenX intentionally omitted).
   - `stack.ops = [ {endpoint: TokenX, callData: approve(router, type(uint256).max)}, {endpoint: router, callData: swap(TokenX, TokenY, residentAmount, attacker)} ]`, both with `invokeWallet=false`, `stack.signerAddress=address(0)`.
4. Fund the Router with `TokenY` so the swap succeeds, and drive the call through `Hinkal.transact` with a valid proof for the attacker's own (zero-amount) `TokenY` UTXO.
5. Assert: (a) `TokenX.balanceOf(Emporium)` decreases by `residentAmount` with no revert from `BalanceChangeShouldBePositive` and no revert from `Hinkal`'s `balanceDif` check; (b) `TokenY.balanceOf(attacker-controlled recipient)` increases by the swap output; (c) no nullifier tied to `TokenX` was ever inserted and no `amountChanges`/UTXO entry accounts for the `TokenX` movement — demonstrating value left Emporium without being counted by either accounting layer.

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

**File:** circuits/MainEVMCircuit.circom (L144-150)
```text
        // 5) Checking that transaction root hash is legit
        calcEqual[i][j] = ForceEqualIfEnabled();
        calcEqual[i][j].in[0] <== calcTransactionRootHash[i][j].rootHash;
        calcEqual[i][j].in[1] <== rootHashHinkal;
        calcEqual[i][j].enabled <== inAmounts[i][j];
        inTotal += inAmounts[i][j];
      }
```

**File:** circuits/MainEVMCircuit.circom (L171-182)
```text
  component distinctErc20AddressChecks[tokenCount * (tokenCount-1)/2];
  var index = 0;
  for (var i =0; i< tokenCount-1;i++){
    for (var j = i+1; j< tokenCount; j++)
    {
      distinctErc20AddressChecks[index] = IsEqual();
      distinctErc20AddressChecks[index].in[0] <== erc20TokenAddresses[i];
      distinctErc20AddressChecks[index].in[1] <== erc20TokenAddresses[j];
      distinctErc20AddressChecks[index].out === 0;
      index++;
    }
  }
```

**File:** contracts/HinkalHelper.sol (L64-71)
```text
    function dimensionsCheck(
        CircomData calldata circomData,
        Dimensions calldata dimensions
    ) internal pure {
        require(
            circomData.erc20TokenAddresses.length == dimensions.tokenNumber,
            "erc20TokenAddresses number should be equal to token number"
        );
```
