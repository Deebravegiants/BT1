### Title
Direct theft of ERC20 dust stranded on `EmporiumUpgradeable` via unchecked `op.endpoint.call` in the empty-`erc20TokenAddresses` "min-circuit" path - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol::runAction)

### Summary
When `circomData.erc20TokenAddresses` is empty and `externalActionId == HINKAL_EMPORIUM_ACTION_ID`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, which only constrains `emporiumMessage`, `timeStamp`, and `calldataHash` in the circuit's public inputs, leaving `op.endpoint`/`op.callData` and any token balance movement completely unconstrained by the proof or by any on-chain balance equality. An attacker can set `stack.ops[i].endpoint` to an arbitrary ERC20 token that happens to hold dust on `EmporiumUpgradeable` and `callData = transfer(attacker, residualBalance)`, and no code path checks that transfer because both `Hinkal.transact`'s `getBalancesForArray` loop and `EmporiumUpgradeable.runAction`'s `balancesBefore/After` loop iterate only over `circomData.erc20TokenAddresses`, which is empty.

### Finding Description
**Broken equality:** tokens leaving `EmporiumUpgradeable` via `op.endpoint.call(callData)` (= `residualBalance`) should equal `-deltaAmountChanges` summed for that token, but since `token ∉ circomData.erc20TokenAddresses` (empty array), the right-hand side is never even evaluated (0 terms), so `residualBalance != 0` goes completely unaccounted for.

**Code path:**
1. `CircomDataBuilder.formInputForCircom` [1](#0-0)  special-cases `HINKAL_EMPORIUM_ACTION_ID` with an empty `erc20TokenAddresses` array and calls `formInputEmporiumMin`, which produces a public-input vector containing only `emporiumMessage`, `timeStamp`, `calldataHash` [2](#0-1) . No `erc20TokenAddresses`, `amountChanges`, nullifiers, or commitments are part of the proof's public inputs in this mode, so the ZK proof places zero constraints on what `EmporiumUpgradeable.runAction` actually does.
2. `Hinkal.transact` computes `oldBalances`/`newBalances` via `getBalancesForArray(circomData.erc20TokenAddresses)` [3](#0-2)  and then loops `for (uint64 i; i < circomData.erc20TokenAddresses.length; i++)` to enforce the balance-diff equality [4](#0-3) . With an empty array this loop body never executes — no check exists for any token not listed.
3. `EmporiumUpgradeable.runAction` executes `stack.ops` via `op.endpoint.call{value: op.value}(op.callData)` [5](#0-4) , with `op.endpoint` and `op.callData` fully attacker-controlled (only guarded against re-entering `callHinkalWallet`/`doSendToRelay` selectors, not against arbitrary ERC20 calls). Its own `balancesBefore`/`balancesAfter` reconciliation loop (lines 85-160) is likewise scoped to `circomData.erc20TokenAddresses`, so a token excluded from that array is never priced or checked.
4. The attacker's own signature covers `EMPORIUM_SIGNATURE_TYPEHASH` over `ops`, so `verifyWallet` doesn't stop this because the attacker is signing their own crafted ops (`stack.signerAddress` can just be `address(0)` to skip signature verification entirely, since `verifyWallet` returns early when `signerAddress == address(0)` [6](#0-5) ).

**Attacker's exact call:** attacker deposits/owns their own trivial UTXO, builds `CircomData` with `erc20TokenAddresses = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalActionMetadata` encoding an `EmporiumStack` with one `op = {endpoint: token, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, residualBalance))}`, generates a valid proof for the min-circuit (which only needs to satisfy `emporiumMessage`/`timeStamp`/`calldataHash`), and calls `Hinkal.transact`.

**Why guards fail:** `performHinkalChecks` → `dimensionsCheck` only requires internal array-length consistency relative to `dimensions.tokenNumber` (which the attacker also sets to 0) [7](#0-6) ; it does not require `erc20TokenAddresses` to include every token an emporium op touches. `checkOnchainCreation` and `verifyProof` operate purely over the (empty) declared token set. None of these mechanisms inspect `op.endpoint`/`op.callData` inside `externalActionMetadata`.

### Impact Explanation
The attacker directly steals ERC20 tokens (`residualBalance`) belonging to `EmporiumUpgradeable`'s trust balance — dust left behind from another user's earlier incomplete/partial swap or transfer — and routes it straight to their own EOA, entirely outside of Hinkal's shielded-balance accounting. This is theft of another user's stranded funds held in trust by the protocol, matching the Critical category ("direct theft of shielded or in-flight user funds"). The attack is repeatable for every token that accumulates dust on `EmporiumUpgradeable` and does not require compromising any privileged role.

### Likelihood Explanation
Preconditions: (1) `EmporiumUpgradeable` must hold a nonzero ERC20 balance of some token from a prior transaction (dust is a realistic byproduct of partial swaps, rounding, or failed `handleOut` transfers where `balanceChange` computations leave leftover wei); (2) the attacker only needs to generate one proof for the "min-circuit"/`HINKAL_EMPORIUM_ACTION_ID` path with an empty token array — no special privileges, no victim cooperation, and cost is limited to gas plus proof generation. This is a low-cost, fully attacker-controlled, repeatable exploit once dust exists.

### Recommendation
Do not allow `EmporiumOperation.endpoint` in the min-circuit (empty `erc20TokenAddresses`) path to be an arbitrary address performing raw ERC20 calls. Either (a) disallow the empty-token-array optimization whenever `stack.ops` contains non-zero-value calls to token-like/arbitrary contracts, (b) require every ERC20 token address touched by any `op.endpoint`/decoded `callData` selector (`transfer`/`transferFrom`/`approve`, etc.) to be present in `circomData.erc20TokenAddresses` so it's captured by the `balancesBefore`/`balancesAfter` reconciliation, or (c) restrict `formInputEmporiumMin`/empty-array mode to a strict allowlist of known-safe router/DEX call patterns validated against `circomData.erc20TokenAddresses` regardless of array length.

### Proof of Concept
Hardhat fork test plan:
1. Deploy `MockERC20`, mint `residualBalance` directly to the `EmporiumUpgradeable` proxy address (simulating dust from an unrelated earlier user's swap).
2. As the attacker, build `CircomData` with `erc20TokenAddresses = []`, `dimensions.tokenNumber = 0`, `externalActionData = {externalAddress: EmporiumUpgradeable, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack({ops: [{endpoint: mockERC20, invokeWallet: false, value: 0, callData: transfer(attacker, residualBalance)}], signerAddress: address(0), maxFee: 0, deadline: <future>}))}`.
3. Generate a real proof for the min-circuit satisfying only `emporiumMessage`, `timeStamp`, `calldataHash` (per `formInputEmporiumMin`).
4. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from the attacker.
5. Assert: `mockERC20.balanceOf(attacker) == residualBalance` after the call, `mockERC20.balanceOf(EmporiumUpgradeable) == 0`, and that `circomData.erc20TokenAddresses` never contained `mockERC20` — i.e., the balance-diff equality in both `Hinkal.transact` (lines 97-146) and `EmporiumUpgradeable.runAction` (lines 132-151) executed zero iterations and thus never priced or constrained this token movement.

### Citations

**File:** contracts/CircomDataBuilder.sol (L138-148)
```text
    ) internal pure returns (uint256[] memory) {
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
```

**File:** contracts/CircomDataBuilder.sol (L150-161)
```text
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

**File:** contracts/Hinkal.sol (L78-90)
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
```

**File:** contracts/Hinkal.sol (L97-146)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L103-117)
```text
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

**File:** contracts/HinkalHelper.sol (L64-90)
```text
    function dimensionsCheck(
        CircomData calldata circomData,
        Dimensions calldata dimensions
    ) internal pure {
        require(
            circomData.erc20TokenAddresses.length == dimensions.tokenNumber,
            "erc20TokenAddresses number should be equal to token number"
        );
        require(
            circomData.amountChanges.length == dimensions.tokenNumber,
            "AmountChanges number should be equal to token number"
        );

        require(
            circomData.onChainCreation.length == dimensions.tokenNumber,
            "onchain creation is equal to tokens count"
        );

        require(
            circomData.slippageValues.length == dimensions.tokenNumber,
            "slippageValues length should be equal to tokens count"
        );

        require(
            circomData.inputNullifiers.length == dimensions.tokenNumber,
            "InputNullifiers number should be equal to token number"
        );
```
